
use crate::sexp::{ParseError, SExp};

use super::{AstMeta, Expr, PropOpExpr, RefExpr, Theorem};

#[derive(Debug)]
pub enum Error {
    UnexpectedPropOpKeyword,
    Convert(ParseError),
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{:?}", self)
    }
}

impl std::error::Error for Error { }

impl From<ParseError> for Error {
    fn from(value: ParseError) -> Self {
        Error::Convert(value)
    }
}

pub type Result<T> = std::result::Result<T, Error>;

pub trait FromSexp : Sized {
    fn from_sexp(sexp: &SExp, meta: &mut AstMeta) -> Result<Self>;
}

pub trait ToSexp {
    fn to_sexp(&self, meta: &AstMeta) -> SExp;
}

impl FromSexp for Theorem {

    fn from_sexp(expr: &SExp, meta: &mut AstMeta) -> Result<Theorem> {
        let l = expr.as_list()?;
        let _kw = l.get(0)?.as_keyword("defthm")?;
        let name = l.get(1)?.as_identifier()?;
        let body = Expr::from_sexp(l.get(2)?, meta)?;
        Ok(Theorem {
            name: meta.get_or_intern(&name.text),
            body,
        })
    }

}

impl FromSexp for PropOpExpr {

    fn from_sexp(expr: &SExp, meta: &mut AstMeta) -> Result<PropOpExpr> {
        let l = expr.as_list()?;
        let kw = l.get(0)?.as_identifier()?;
        let name = meta.get_or_intern(&kw.text);
        let op_desc = match meta.get_op_desc_with_symbol(name) {
            Some(desc) => desc,
            None => return Err(Error::UnexpectedPropOpKeyword),
        };
        let op_id = op_desc.id;
        let mut args = Vec::new();
        for i in 0..op_desc.arity {
            let arg = Expr::from_sexp(l.get((i+1).into())?, meta)?;
            args.push(arg);
        }
        // TODO assert expr is now empty
        Ok(PropOpExpr {
            op_id,
            args,
        })
    }

}

impl FromSexp for RefExpr {

    fn from_sexp(expr: &SExp, meta: &mut AstMeta) -> Result<RefExpr> {
        let ident = expr.as_identifier()?;
        Ok(RefExpr { name: meta.get_or_intern(&ident.text) })
    }

}

impl FromSexp for Expr {

    fn from_sexp(sexp: &SExp, meta: &mut AstMeta) -> Result<Expr> {
        Ok(match sexp {
            SExp::Integer(..) => unimplemented!(),
            SExp::Identifier(..) => RefExpr::from_sexp(sexp, meta)?.into(),
            SExp::List(..) => PropOpExpr::from_sexp(sexp, meta)?.into(),
        })
    }

}

impl ToSexp for Expr  {

    fn to_sexp(&self, meta: &AstMeta) -> SExp {
        match self {
            Self::Ref(inner) => inner.to_sexp(meta),
            Self::PropOp(inner) => inner.to_sexp(meta),
        }
    }
}

impl ToSexp for RefExpr {

    fn to_sexp(&self, meta: &AstMeta) -> SExp {
        SExp::ident(meta.resolve_name(self.name).unwrap())
    }

}

impl ToSexp for PropOpExpr {

    fn to_sexp(&self, meta: &AstMeta) -> SExp {
        let mut v = Vec::new();
        let desc = meta.get_op_desc_with_id(self.op_id).unwrap();
        v.push(SExp::ident(&desc.symbol));
        for arg in &self.args {
            v.push(arg.to_sexp(meta));
        }
        SExp::list(&v)
    }

}

