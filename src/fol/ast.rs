
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Expr {
    Ref(Ref),
    Not(Not),
    Or(Or),
    And(And),
    Implies(Implies),
    Equiv(Equiv),
}

impl Expr {

    pub fn name<S: Into<String>>(s: S) -> Expr {
        Expr::Ref(Ref { name: s.into() })
    }

    pub fn and(left: Expr, right: Expr) -> Expr {
        Expr::And(And {
            left: Box::new(left),
            right: Box::new(right),
        })
    }

    pub fn or(left: Expr, right: Expr) -> Expr {
        Expr::Or(Or {
            left: Box::new(left),
            right: Box::new(right),
        })
    }

    pub fn not(expr: Expr) -> Expr {
        Expr::Not(Not { expr: Box::new(expr) })
    }

    pub fn implies(premise: Expr, conclusion: Expr) -> Expr {
        Expr::Implies(Implies {
            premise: Box::new(premise),
            conclusion: Box::new(conclusion),
        })
    }

    pub fn equiv(left: Expr, right: Expr) -> Expr {
        Expr::Equiv(Equiv {
            left: Box::new(left),
            right: Box::new(right),
        })
    }

}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Theorem {
    pub name: String,
    pub body: Expr,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Ref {
    pub name: String,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct And {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Not {
    pub expr: Box<Expr>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Or {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Implies {
    pub premise: Box<Expr>,
    pub conclusion: Box<Expr>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
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

