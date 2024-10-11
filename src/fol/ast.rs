
#[derive(Debug)]
pub enum Expr {
    Ref(Ref),
    Not(Not),
    Or(Or),
    And(And),
    Implies(Implies),
    Equiv(Equiv),
}

#[derive(Debug)]
pub struct Theorem {
    pub name: String,
    pub body: Expr,
}

#[derive(Debug)]
pub struct Ref {
    pub name: String,
}

#[derive(Debug)]
pub struct And {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
}

#[derive(Debug)]
pub struct Not {
    pub expr: Box<Expr>,
}

#[derive(Debug)]
pub struct Or {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
}

#[derive(Debug)]
pub struct Implies {
    pub premise: Box<Expr>,
    pub conclusion: Box<Expr>,
}

#[derive(Debug)]
pub struct Equiv {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
}

impl From<Ref> for Expr {
    fn from(value: Ref) -> Self {
        Expr::Ref(value)
    }
}

impl From<And> for Expr {
    fn from(value: And) -> Self {
        Expr::And(value)
    }
}

impl From<Or> for Expr {
    fn from(value: Or) -> Self {
        Expr::Or(value)
    }
}

impl From<Implies> for Expr {
    fn from(value: Implies) -> Self {
        Expr::Implies(value)
    }
}

impl From<Not> for Expr {
    fn from(value: Not) -> Self {
        Expr::Not(value)
    }
}

impl From<Equiv> for Expr {
    fn from(value: Equiv) -> Self {
        Expr::Equiv(value)
    }
}

