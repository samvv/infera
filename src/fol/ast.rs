
use bitvec::{bitvec, vec::BitVec};
use lazy_static::lazy_static;

#[derive(Clone)]
pub struct OpDesc {
    pub id: usize,
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
            id: 0,
            arity: 2,
            symbol: "and".to_string(),
            table: AND_TABLE.clone(),
        });

        ops.push(OpDesc {
            id: 1,
            arity: 2,
            symbol: "or".to_string(),
            table: OR_TABLE.clone(),
        });

        ops.push(OpDesc {
            id: 2,
            arity: 2,
            symbol: "=>".to_string(),
            table: IMPLIES_TABLE.clone(),
        });

        ops.push(OpDesc {
            id: 3,
            arity: 2,
            symbol: "equiv".to_string(),
            table: EQUIV_TABLE.clone(),
        });

        ops.push(OpDesc {
            id: 4,
            arity: 1,
            symbol: "not".to_string(),
            table: NOT_TABLE.clone(),
        });

        ops
    };

}

#[derive(Clone, Debug, Ord, PartialOrd, Eq, PartialEq, Hash)]
pub enum Expr {
    Ref(RefExpr),
    PropOp(PropOpExpr),
}

impl Expr {

    pub fn name<S: Into<String>>(s: S) -> Expr {
        Expr::Ref(RefExpr { name: s.into() })
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
    pub name: String,
    pub body: Expr,
}

#[derive(Clone, Debug, Ord, PartialOrd, Eq, PartialEq, Hash)]
pub struct RefExpr {
    pub name: String,
}

#[derive(Clone, Debug, Ord, PartialOrd, Eq, PartialEq, Hash)]
pub struct PropOpExpr {
    pub op_id: usize,
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
