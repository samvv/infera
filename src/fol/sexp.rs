
use crate::sexp::{ParseError, SExp};

use super::{And, Equiv, Expr, Implies, Not, Or, Ref, Theorem};

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

impl Parse for And {

    fn parse(expr: &SExp) -> Result<Self> {
        let l = expr.as_list()?;
        let _kw = l.get(0)?.as_keyword(AND_NAME)?;
        let left = Expr::parse(l.get(1)?)?;
        let right = Expr::parse(l.get(2)?)?;
        // TODO assert len(l) == 3
        Ok(And {
            left: Box::new(left),
            right: Box::new(right)
        })
    }

}

impl Parse for Or {

    fn parse(expr: &SExp) -> Result<Self> {
        let l = expr.as_list()?;
        let _kw = l.get(0)?.as_keyword(OR_NAME)?;
        let left = Expr::parse(l.get(1)?)?;
        let right = Expr::parse(l.get(2)?)?;
        // TODO assert len(l) == 3
        Ok(Or {
            left: Box::new(left),
            right: Box::new(right)
        })
    }

}

impl Parse for Implies {

    fn parse(expr: &SExp) -> Result<Self> {
        let l = expr.as_list()?;
        let _kw = l.get(0)?.as_keyword(IMPLIES_NAME)?;
        let left = Expr::parse(l.get(1)?)?;
        let right = Expr::parse(l.get(2)?)?;
        // TODO assert len(l) == 3
        Ok(Implies {
            premise: Box::new(left),
            conclusion: Box::new(right)
        })
    }

}

impl Parse for Equiv {

    fn parse(expr: &SExp) -> Result<Self> {
        let l = expr.as_list()?;
        let _kw = l.get(0)?.as_keyword(EQUIV_NAME)?;
        let left = Expr::parse(l.get(1)?)?;
        let right = Expr::parse(l.get(2)?)?;
        // TODO assert len(l) == 3
        Ok(Equiv {
            left: Box::new(left),
            right: Box::new(right)
        })
    }

}

impl Parse for Not {

    fn parse(expr: &SExp) -> Result<Self> {
        let l = expr.as_list()?;
        let _kw = l.get(0)?.as_keyword("not")?;
        let expr = Expr::parse(l.get(1)?)?;
        Ok(Not {
            expr: Box::new(expr),
        })
    }

}

impl Parse for Expr {

    fn parse(sexp: &SExp) -> Result<Expr> {
        Ok(match sexp {
            SExp::Integer(int) => unimplemented!(),
            SExp::Identifier(ident) => Expr::Ref(Ref { name: ident.text.clone() }),
            SExp::List(l) => {
                match l.get(0)?.as_identifier()?.text.as_str() {
                    AND_NAME => And::parse(sexp)?.into(),
                    OR_NAME => Or::parse(sexp)?.into(),
                    NOT_NAME => Not::parse(sexp)?.into(),
                    IMPLIES_NAME => Implies::parse(sexp)?.into(),
                    EQUIV_NAME => Equiv::parse(sexp)?.into(),
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

