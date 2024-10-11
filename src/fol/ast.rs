
#[derive(Clone, Debug, Eq, PartialEq, Hash)]
pub enum Expr {
    Ref(RefExpr),
    Not(NotExpr),
    Or(OrExpr),
    And(AndExpr),
    Implies(ImpliesExpr),
    Equiv(EquivExpr),
}

impl Expr {

    pub fn name<S: Into<String>>(s: S) -> Expr {
        Expr::Ref(RefExpr { name: s.into() })
    }

    pub fn and(left: Expr, right: Expr) -> Expr {
        Expr::And(AndExpr {
            left: Box::new(left),
            right: Box::new(right),
        })
    }

    pub fn or(left: Expr, right: Expr) -> Expr {
        Expr::Or(OrExpr {
            left: Box::new(left),
            right: Box::new(right),
        })
    }

    pub fn not(expr: Expr) -> Expr {
        Expr::Not(NotExpr { expr: Box::new(expr) })
    }

    pub fn implies(premise: Expr, conclusion: Expr) -> Expr {
        Expr::Implies(ImpliesExpr {
            premise: Box::new(premise),
            conclusion: Box::new(conclusion),
        })
    }

    pub fn equiv(left: Expr, right: Expr) -> Expr {
        Expr::Equiv(EquivExpr {
            left: Box::new(left),
            right: Box::new(right),
        })
    }

}

#[derive(Clone, Debug, Eq, PartialEq, Hash)]
pub struct Theorem {
    pub name: String,
    pub body: Expr,
}

#[derive(Clone, Debug, Eq, PartialEq, Hash)]
pub struct RefExpr {
    pub name: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Hash)]
pub struct AndExpr {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
}

#[derive(Clone, Debug, Eq, PartialEq, Hash)]
pub struct NotExpr {
    pub expr: Box<Expr>,
}

#[derive(Clone, Debug, Eq, PartialEq, Hash)]
pub struct OrExpr {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
}

#[derive(Clone, Debug, Eq, PartialEq, Hash)]
pub struct ImpliesExpr {
    pub premise: Box<Expr>,
    pub conclusion: Box<Expr>,
}

#[derive(Clone, Debug, Eq, PartialEq, Hash)]
pub struct EquivExpr {
    pub left: Box<Expr>,
    pub right: Box<Expr>,
}

impl From<RefExpr> for Expr {
    fn from(value: RefExpr) -> Self {
        Expr::Ref(value)
    }
}

impl From<AndExpr> for Expr {
    fn from(value: AndExpr) -> Self {
        Expr::And(value)
    }
}

impl From<OrExpr> for Expr {
    fn from(value: OrExpr) -> Self {
        Expr::Or(value)
    }
}

impl From<ImpliesExpr> for Expr {
    fn from(value: ImpliesExpr) -> Self {
        Expr::Implies(value)
    }
}

impl From<NotExpr> for Expr {
    fn from(value: NotExpr) -> Self {
        Expr::Not(value)
    }
}

impl From<EquivExpr> for Expr {
    fn from(value: EquivExpr) -> Self {
        Expr::Equiv(value)
    }
}

