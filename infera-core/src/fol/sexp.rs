
use crate::sexp::{List, ParseError, Sexp};

use super::{AstMeta, Expr, PredBody, PropOpExpr, RefExpr, Theorem};

pub const EXISTS_NAME: &str = "exists";
pub const FORALL_NAME: &str = "forall";

#[derive(Debug)]
pub enum Error {
    UnexpectedPropOpKeyword,
    InvalidSExp,
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
    fn from_sexp(sexp: &Sexp, meta: &mut AstMeta) -> Result<Self>;
}

pub trait ToSexp {
    fn to_sexp(&self, meta: &AstMeta) -> Sexp;
}

impl FromSexp for Theorem {

    fn from_sexp(expr: &Sexp, meta: &mut AstMeta) -> Result<Theorem> {
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

    fn from_sexp(expr: &Sexp, meta: &mut AstMeta) -> Result<PropOpExpr> {
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

    fn from_sexp(sexp: &Sexp, meta: &mut AstMeta) -> Result<RefExpr> {
        let ident = sexp.as_identifier()?;
        Ok(RefExpr { name: meta.get_or_intern(&ident.text) })
    }

}

fn pred_body_from_list(l: &List, meta: &mut AstMeta) -> Result<PredBody> {
    let name = l.get(1)?.as_identifier()?;
    let expr = Expr::from_sexp(l.get(2)?, meta)?;
    Ok(PredBody { name: meta.get_or_intern(&name.text), expr: Box::new(expr) })
}

impl FromSexp for Expr {

    fn from_sexp(sexp: &Sexp, meta: &mut AstMeta) -> Result<Expr> {
        Ok(match sexp {
            Sexp::Integer(..) => unimplemented!(),
            Sexp::Identifier(..) => RefExpr::from_sexp(sexp, meta)?.into(),
            Sexp::List(l) if l.elements.len() > 1 => {
                let kw = l.get(0)?.as_identifier()?.text.as_str();
                match kw {
                    EXISTS_NAME => Expr::Exists(pred_body_from_list(l, meta)?),
                    FORALL_NAME => Expr::Forall(pred_body_from_list(l, meta)?),
                    _ => PropOpExpr::from_sexp(sexp, meta)?.into()
                }
            },
            _ => return Err(Error::InvalidSExp),
        })
    }

}

fn pred_to_sexp(name: &str, body: &PredBody, meta: &AstMeta) -> Sexp {
    let mut v = Vec::new();
    v.push(Sexp::ident(name));
    v.push(Sexp::ident(meta.resolve_name(body.name).unwrap()));
    v.push(body.expr.to_sexp(meta));
    Sexp::list(v)
}

impl ToSexp for Expr  {

    fn to_sexp(&self, meta: &AstMeta) -> Sexp {
        match self {
            Self::Ref(inner) => inner.to_sexp(meta),
            Self::PropOp(inner) => inner.to_sexp(meta),
            Self::Forall(inner) => pred_to_sexp(EXISTS_NAME, inner, meta),
            Self::Exists(inner) => pred_to_sexp(EXISTS_NAME, inner, meta),
        }
    }

}

impl ToSexp for RefExpr {

    fn to_sexp(&self, meta: &AstMeta) -> Sexp {
        Sexp::ident(meta.resolve_name(self.name).unwrap())
    }

}

impl ToSexp for PropOpExpr {

    fn to_sexp(&self, meta: &AstMeta) -> Sexp {
        let mut v = Vec::new();
        let desc = meta.get_op_desc_with_id(self.op_id).unwrap();
        v.push(Sexp::ident(&desc.symbol));
        for arg in &self.args {
            v.push(arg.to_sexp(meta));
        }
        Sexp::list(v)
    }

}

