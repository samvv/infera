use std::collections::{hash_map::Entry, HashMap};

use super::{And, Equiv, Expr, Implies, Not, Or, Ref};

pub struct Rule {
    pattern: Expr,
    expr: Expr,
}

impl Rule {

    pub fn new(pattern: Expr, expr: Expr) -> Rule {
        Self {
            pattern,
            expr,
        }
    }

}

type Subst = HashMap<String, Expr>;

fn unify_impl(left: &Expr, right: &Expr, sub: &mut Subst) -> bool {
    match (left, right) {
        (Expr::Ref(Ref { name: a }), _) => {
            match sub.entry(a.clone()) {
                Entry::Vacant(entry) => { entry.insert(right.clone()); },
                Entry::Occupied(entry) if entry.get() == right => {},
                _ => return false,
            }
            true
        }
        (Expr::Not(Not { expr: inner_1 }), Expr::Not(Not { expr: inner_2 })) => unify_impl(inner_1, inner_2, sub),
        (Expr::And(And { left: left_1, right: right_1 }), Expr::And(And { left: left_2, right: right_2 })) =>
            unify_impl(left_1, left_2, sub) && unify_impl(right_1, right_2, sub),
        (Expr::Or(Or { left: left_1, right: right_1 }), Expr::Or(Or { left: left_2, right: right_2 })) =>
            unify_impl(left_1, left_2, sub) && unify_impl(right_1, right_2, sub),
        (Expr::Implies(Implies { premise: left_1, conclusion: right_1 }), Expr::Implies(Implies { premise: left_2, conclusion: right_2 })) =>
            unify_impl(left_1, left_2, sub) && unify_impl(right_1, right_2, sub),
        (Expr::Equiv(Equiv { left: left_1, right: right_1 }), Expr::Equiv(Equiv { left: left_2, right: right_2 })) =>
            unify_impl(left_1, left_2, sub) && unify_impl(right_1, right_2, sub),
        _ => false,
    }
}

pub fn unify(left: &Expr, right: &Expr) -> Option<Subst> {
    let mut subst = Subst::new();
    if unify_impl(left, right, &mut subst) {
        Some(subst)
    } else {
        None
    }
}

pub fn apply(sub: &Subst, expr: &Expr) -> Expr {
    match expr {
        Expr::Ref(Ref { name }) => match sub.get(name) {
            Some(new_expr) => new_expr.clone(),
            None => expr.clone(),
        },
        Expr::Not(Not { expr }) => Expr::not(apply(sub, expr)),
        Expr::Or(Or { left, right }) => Expr::or(apply(sub, left), apply(sub, right)),
        Expr::And(And { left, right }) => Expr::and(apply(sub, left), apply(sub, right)),
        Expr::Implies(Implies { premise, conclusion }) => Expr::implies(apply(sub, premise), apply(sub, conclusion)),
        Expr::Equiv(Equiv { left, right }) => Expr::equiv(apply(sub, left), apply(sub, right)),
    }
}

pub struct Rewriter {
    rules: Vec<Rule>,
}

impl Rewriter {

    pub fn new() -> Self {
        Self {
            rules: Vec::new(),
        }
    }

    pub fn add_rule(&mut self, rule: Rule) {
        self.rules.push(rule);
    }

    pub fn expand(&self, expr: Expr) -> Vec<Expr> {
        let mut out = Vec::new();
        for rule in &self.rules {
            if let Some(sub) = unify(&rule.pattern, &expr) {
                out.push(apply(&sub, &rule.expr));
            }
        }
        out
    }

    pub fn prove(&mut self, expr: Expr, goal: Expr) {
        unimplemented!()
    }

}

