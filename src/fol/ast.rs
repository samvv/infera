
use std::collections::HashMap;

use bitvec::{bitvec, vec::BitVec};
use lazy_static::lazy_static;
use string_interner::{DefaultStringInterner, DefaultSymbol, StringInterner, Symbol};

pub type OpId = u32;

#[derive(Clone)]
pub struct OpDesc {
    pub id: OpId,
    pub arity: u16,
    pub symbol: String,
    pub table: TruthTable,
}

#[derive(Clone, Eq, PartialEq)]
pub struct TruthTable {
    output: BitVec,
}

impl TruthTable {

    pub fn new(output: BitVec) -> Self {
        Self {
            output,
        }
    }

    pub fn with_var_count(n: u32) -> Self {
        Self {
            output: bitvec![0; usize::pow(2, n) ]
        }
    }

    pub fn var_count(&self) -> u32 {
        usize::ilog2(self.output.len())
    }

    fn index(&self, values: &[bool]) -> usize {
        let mut k = 0;
        for (i, b) in values.iter().enumerate() {
            if *b {
                k += usize::pow(2, i.try_into().unwrap());
            }
        }
        k
    }

    pub fn set(&mut self, values: &[bool], truthy: bool) {
        let k = self.index(values);
        self.output.set(k, truthy);
    }

    pub fn get(&self, values: &[bool]) -> bool {
        let k = self.index(values);
        *self.output.get(k).unwrap()
    }

}

pub const AND_ID: OpId = 0;
pub const OR_ID: OpId = 1;
pub const NOT_ID: OpId = 2;
pub const IMPLIES_ID: OpId = 3;
pub const EQUIV_ID: OpId = 4;

lazy_static! {

    pub static ref NOT_TABLE: TruthTable = {
        let mut table = TruthTable::with_var_count(1);
        table.set(&[true], true);
        table
    };

    pub static ref AND_TABLE: TruthTable = {
        let mut table = TruthTable::with_var_count(2);
        table.set(&[true, true], true);
        table
    };

    pub static ref OR_TABLE: TruthTable = {
        let mut table = TruthTable::with_var_count(2);
        table.set(&[false, true], true);
        table.set(&[true, false], true);
        table.set(&[true, true], true);
        table
    };

    pub static ref IMPLIES_TABLE: TruthTable = {
        let mut table = TruthTable::with_var_count(2);
        table.set(&[false, false], true);
        table.set(&[false, true], true);
        table.set(&[true, true], true);
        table
    };

    pub static ref EQUIV_TABLE: TruthTable = {
        let mut table = TruthTable::with_var_count(2);
        table.set(&[false, false], true);
        table.set(&[true, true], true);
        table
    };

    pub static ref XOR_TABLE: TruthTable = {
        let mut table = TruthTable::with_var_count(2);
        table.set(&[false, true], true);
        table.set(&[true, false], true);
        table
    };

    pub static ref BUILTIN_OPS: Vec<OpDesc> = {

        let mut ops = Vec::new();

        ops.push(OpDesc {
            id: AND_ID,
            arity: 2,
            symbol: "and".to_string(),
            table: AND_TABLE.clone(),
        });

        ops.push(OpDesc {
            id: OR_ID,
            arity: 2,
            symbol: "or".to_string(),
            table: OR_TABLE.clone(),
        });

        ops.push(OpDesc {
            id: IMPLIES_ID,
            arity: 2,
            symbol: "=>".to_string(),
            table: IMPLIES_TABLE.clone(),
        });

        ops.push(OpDesc {
            id: EQUIV_ID,
            arity: 2,
            symbol: "equiv".to_string(),
            table: EQUIV_TABLE.clone(),
        });

        ops.push(OpDesc {
            id: NOT_ID,
            arity: 1,
            symbol: "not".to_string(),
            table: NOT_TABLE.clone(),
        });

        ops
    };

}

pub struct AstMeta {
    op_desc_by_id: HashMap<OpId, OpDesc>,
    op_desc_by_symbol: HashMap<Name, OpDesc>,
    interner: DefaultStringInterner,
}

pub type Name = DefaultSymbol;

impl AstMeta {

    pub fn new() -> Self {
        Self {
            op_desc_by_symbol: HashMap::new(),
            op_desc_by_id: HashMap::new(),
            interner: Default::default(),
        }
    }

    pub fn add_op_desc(&mut self, desc: OpDesc) {
        self.op_desc_by_id.insert(desc.id, desc.clone());
        let sym = self.get_or_intern(&desc.symbol);
        self.op_desc_by_symbol.insert(sym, desc);
    }

    pub fn get_op_desc_with_id(&self, id: OpId) -> Option<&OpDesc> {
        self.op_desc_by_id.get(&id)
    }

    pub fn get_op_desc_with_symbol(&self, symbol: Name) -> Option<&OpDesc> {
        self.op_desc_by_symbol.get(&symbol)
    }

    pub fn get_or_intern<S: AsRef<str>>(&mut self, s: S) -> Name {
        self.interner.get_or_intern(s)
    }

    pub fn resolve_name(&self, sym: Name) -> Option<&str> {
        self.interner.resolve(sym)
    }

}

#[derive(Clone, Debug, Ord, PartialOrd, Eq, PartialEq, Hash)]
pub enum Expr {
    Ref(RefExpr),
    PropOp(PropOpExpr),
}

impl Expr {

    pub fn name(name: Name) -> Expr {
        Expr::Ref(RefExpr { name })
    }

    pub fn len(&self) -> u32 {
        match self {
            Expr::Ref(..) => 1,
            Expr::PropOp(op) => 1 + op.args.iter().map(|arg| arg.len()).sum::<u32>(),
        }
    }

}

#[derive(Clone, Debug, Ord, PartialOrd, Eq, PartialEq, Hash)]
pub struct Theorem {
    pub name: Name,
    pub body: Expr,
}

#[derive(Clone, Debug, Ord, PartialOrd, Eq, PartialEq, Hash)]
pub struct RefExpr {
    pub name: Name,
}

#[derive(Clone, Debug, Ord, PartialOrd, Eq, PartialEq, Hash)]
pub struct PropOpExpr {
    pub op_id: OpId,
    pub args: Vec<Expr>,
}

impl From<RefExpr> for Expr {
    fn from(value: RefExpr) -> Self {
        Expr::Ref(value)
    }
}

impl From<PropOpExpr> for Expr {
    fn from(value: PropOpExpr) -> Self {
        Expr::PropOp(value)
    }
}
