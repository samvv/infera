use super::Sexp;


#[derive(Clone, Debug)]
pub enum Pattern {
    Bind(BindPattern),
}

#[derive(Clone, Debug)]
pub struct BindPattern {
    pub name: String,
}

#[derive(Clone, Debug)]
pub enum Expr {
    Ref(RefExpr),
    Call(CallExpr),
    Begin(BeginExpr),
}

#[derive(Clone, Debug)]
pub struct RefExpr {
    pub name: String,
}

#[derive(Clone, Debug)]
pub struct CallExpr {
    pub func: Box<Expr>,
    pub args: Vec<Expr>,
}

#[derive(Clone, Debug)]
pub struct BeginExpr {
    pub elements: Vec<Expr>,
    pub last: Box<Expr>,
}

#[derive(Clone, Debug)]
pub enum Decl {
    Var(VarDecl),
    Func(FuncDecl),
}

#[derive(Clone, Debug)]
pub struct VarDecl {
    pub name: String,
    pub expr: Expr,
}

#[derive(Clone, Debug)]
pub struct FuncDecl {
    pub name: String,
    pub params: Vec<Pattern>,
    pub body: Expr,
}

#[derive(Clone, Debug)]
pub enum ProgElement {
    Decl(Decl),
    Expr(Expr),
}

#[derive(Clone, Debug)]
pub struct Program {
    pub elements: Vec<ProgElement>,
}

pub trait FromSexp {
    fn from_sexp(sexp: &Sexp) -> Self;
}

impl FromSexp for FuncDecl {
    fn from_sexp(sexp: &Sexp) -> Self {
        match_sexp!(sexp {
            (define (+name:Sident +params:Pattern...) +body) => {
                FuncDecl {
                    name,
                    params,
                    body
                }
            }
        })
    }
}
