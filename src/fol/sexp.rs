
use crate::sexp::{ParseError, SExp};

use super::{AndExpr, EquivExpr, Expr, ImpliesExpr, NotExpr, OrExpr, RefExpr, Theorem};

const NOT_NAME: &str = "not";
const OR_NAME: &str = "or";
const AND_NAME: &str = "and";
const IMPLIES_NAME: &str = "implies";
const EQUIV_NAME: &str = "equiv";

#[derive(Debug)]
pub enum Error {
    Expected(Vec<String>, String),
    Convert(ParseError),
}

impl From<ParseError> for Error {
    fn from(value: ParseError) -> Self {
        Error::Convert(value)
    }
}

pub type Result<T> = std::result::Result<T, Error>;

pub trait Parse : Sized {
    fn parse(expr: &SExp) -> Result<Self>;
}

pub trait ToSexp {
    fn to_sexp(&self) -> SExp;
}

impl Parse for Theorem {

    fn parse(expr: &SExp) -> Result<Theorem> {
        let l = expr.as_list()?;
        let _kw = l.get(0)?.as_keyword("defthm")?;
        let name = l.get(1)?.as_identifier()?;
        let body = Expr::parse(l.get(2)?)?;
        Ok(Theorem {
            name: name.text.clone(),
            body,
        })
    }

}

impl Parse for AndExpr {

    fn parse(expr: &SExp) -> Result<Self> {
        let l = expr.as_list()?;
        let _kw = l.get(0)?.as_keyword(AND_NAME)?;
        let left = Expr::parse(l.get(1)?)?;
        let right = Expr::parse(l.get(2)?)?;
        // TODO assert len(l) == 3
        Ok(AndExpr {
            left: Box::new(left),
            right: Box::new(right)
        })
    }

}

impl Parse for OrExpr {

    fn parse(expr: &SExp) -> Result<Self> {
        let l = expr.as_list()?;
        let _kw = l.get(0)?.as_keyword(OR_NAME)?;
        let left = Expr::parse(l.get(1)?)?;
        let right = Expr::parse(l.get(2)?)?;
        // TODO assert len(l) == 3
        Ok(OrExpr {
            left: Box::new(left),
            right: Box::new(right)
        })
    }

}

impl Parse for ImpliesExpr {

    fn parse(expr: &SExp) -> Result<Self> {
        let l = expr.as_list()?;
        let _kw = l.get(0)?.as_keyword(IMPLIES_NAME)?;
        let left = Expr::parse(l.get(1)?)?;
        let right = Expr::parse(l.get(2)?)?;
        // TODO assert len(l) == 3
        Ok(ImpliesExpr {
            premise: Box::new(left),
            conclusion: Box::new(right)
        })
    }

}

impl Parse for EquivExpr {

    fn parse(expr: &SExp) -> Result<Self> {
        let l = expr.as_list()?;
        let _kw = l.get(0)?.as_keyword(EQUIV_NAME)?;
        let left = Expr::parse(l.get(1)?)?;
        let right = Expr::parse(l.get(2)?)?;
        // TODO assert len(l) == 3
        Ok(EquivExpr {
            left: Box::new(left),
            right: Box::new(right)
        })
    }

}

impl Parse for NotExpr {

    fn parse(expr: &SExp) -> Result<Self> {
        let l = expr.as_list()?;
        let _kw = l.get(0)?.as_keyword("not")?;
        let expr = Expr::parse(l.get(1)?)?;
        Ok(NotExpr {
            expr: Box::new(expr),
        })
    }

}

impl Parse for Expr {

    fn parse(sexp: &SExp) -> Result<Expr> {
        Ok(match sexp {
            SExp::Integer(int) => unimplemented!(),
            SExp::Identifier(ident) => Expr::Ref(RefExpr { name: ident.text.clone() }),
            SExp::List(l) => {
                match l.get(0)?.as_identifier()?.text.as_str() {
                    AND_NAME => AndExpr::parse(sexp)?.into(),
                    OR_NAME => OrExpr::parse(sexp)?.into(),
                    NOT_NAME => NotExpr::parse(sexp)?.into(),
                    IMPLIES_NAME => ImpliesExpr::parse(sexp)?.into(),
                    EQUIV_NAME => EquivExpr::parse(sexp)?.into(),
                    name => return Err(Error::Expected(
                        vec![
                            AND_NAME.to_string(),
                            OR_NAME.to_string(),
                            NOT_NAME.to_string(),
                            IMPLIES_NAME.to_string(),
                            EQUIV_NAME.to_string(),
                        ],
                        name.to_owned()
                    )),
                }
            }
        })
    }

}

impl ToSexp for Expr {
    fn to_sexp(&self) -> SExp {
        match self {
            Self::Ref(inner) => inner.to_sexp(),
            Self::And(inner) => inner.to_sexp(),
            Self::Or(inner) => inner.to_sexp(),
            Self::Not(inner) => inner.to_sexp(),
            Self::Implies(inner) => inner.to_sexp(),
            Self::Equiv(inner) => inner.to_sexp(),
        }
    }
}

impl ToSexp for RefExpr {
    fn to_sexp(&self) -> SExp {
        SExp::ident(self.name.clone())
    }
}

impl ToSexp for NotExpr {
    fn to_sexp(&self) -> SExp {
        SExp::list(&[
            SExp::ident(NOT_NAME),
            self.expr.to_sexp()
        ])
    }
}

impl ToSexp for ImpliesExpr {
    fn to_sexp(&self) -> SExp {
        SExp::list(&[
            SExp::ident(IMPLIES_NAME),
            self.premise.to_sexp(),
            self.conclusion.to_sexp(),
        ])
    }
}


impl ToSexp for EquivExpr {
    fn to_sexp(&self) -> SExp {
        SExp::list(&[
            SExp::ident(EQUIV_NAME),
            self.left.to_sexp(),
            self.right.to_sexp(),
        ])
    }
}


impl ToSexp for OrExpr {
    fn to_sexp(&self) -> SExp {
        SExp::list(&[
            SExp::ident(OR_NAME),
            self.left.to_sexp(),
            self.right.to_sexp(),
        ])
    }
}

impl ToSexp for AndExpr {
    fn to_sexp(&self) -> SExp {
        SExp::list(&[
            SExp::ident(AND_NAME),
            self.left.to_sexp(),
            self.right.to_sexp(),
        ])
    }
}
