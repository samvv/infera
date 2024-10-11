
use std::collections::HashMap;

use crate::sexp::{ParseError, SExp};

use super::{Expr, OpDesc, PropOpExpr, RefExpr, Theorem};

#[derive(Debug)]
pub enum Error {
    UnexpectedPropOpKeyword,
    Convert(ParseError),
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        todo!()
    }
}

impl std::error::Error for Error { }

impl From<ParseError> for Error {
    fn from(value: ParseError) -> Self {
        Error::Convert(value)
    }
}

pub type Result<T> = std::result::Result<T, Error>;

pub trait ToSexp {
    fn to_sexp(&self) -> SExp;
}

pub struct Parser<'a> {
    ops: HashMap<String, &'a OpDesc>,
}

impl <'a> Parser<'a> {

    pub fn with_ops(ops: &'a [OpDesc]) -> Self {
        let mut m = HashMap::new();
        for op in ops {
            m.insert(op.symbol.clone(), op);
        }
        Self { ops: m }
    }

    fn find_op(&self, name: &str) -> Option<&'a OpDesc> {
        self.ops.get(name).map(|v| &**v)
    }

    pub fn parse_theorem(&self, expr: &SExp) -> Result<Theorem> {
        let l = expr.as_list()?;
        let _kw = l.get(0)?.as_keyword("defthm")?;
        let name = l.get(1)?.as_identifier()?;
        let body = self.parse_expr(l.get(2)?)?;
        Ok(Theorem {
            name: name.text.clone(),
            body,
        })
    }

    pub fn parse_prop_op(&self, expr: &SExp) -> Result<PropOpExpr> {
        let l = expr.as_list()?;
        let kw = l.get(0)?.as_identifier()?;
        let op_desc = match self.find_op(&kw.text) {
            Some(desc) => desc,
            None => return Err(Error::UnexpectedPropOpKeyword),
        };
        let mut args = Vec::new();
        for i in 0..op_desc.arity {
            let arg = self.parse_expr(l.get((i+1).into())?)?;
            args.push(arg);
        }
        // TODO assert expr is now empty
        Ok(PropOpExpr {
            op_id: op_desc.id,
            args,
        })
    }

    pub fn parse_ref_expr(&self, expr: &SExp) -> Result<RefExpr> {
        let ident = expr.as_identifier()?;
        Ok(RefExpr { name: ident.text.clone() })
    }

    pub fn parse_expr(&self, sexp: &SExp) -> Result<Expr> {
        Ok(match sexp {
            SExp::Integer(int) => unimplemented!(),
            SExp::Identifier(..) => self.parse_ref_expr(sexp)?.into(),
            SExp::List(..) => self.parse_prop_op(sexp)?.into(),
        })
    }

}

impl ToSexp for Expr {
    fn to_sexp(&self) -> SExp {
        match self {
            Self::Ref(inner) => inner.to_sexp(),
            Self::PropOp(inner) => inner.to_sexp(),
        }
    }
}

impl ToSexp for RefExpr {
    fn to_sexp(&self) -> SExp {
        SExp::ident(self.name.clone())
    }
}

impl ToSexp for PropOpExpr {
    fn to_sexp(&self) -> SExp {
        let mut v = Vec::new();
        v.push(SExp::ident(format!("op{}", self.op_id)));
        for arg in &self.args {
            v.push(arg.to_sexp());
        }
        SExp::list(&v)
    }
}

