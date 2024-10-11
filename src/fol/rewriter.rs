use std::{collections::{hash_map::Entry, HashMap, HashSet, VecDeque}, fmt::write};

use super::{AndExpr, EquivExpr, Expr, ImpliesExpr, NotExpr, OrExpr, RefExpr};

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
        (Expr::Ref(RefExpr { name: a }), _) => {
            match sub.entry(a.clone()) {
                Entry::Vacant(entry) => { entry.insert(right.clone()); },
                Entry::Occupied(entry) if entry.get() == right => {},
                _ => return false,
            }
            true
        }
        (Expr::Not(NotExpr { expr: inner_1 }), Expr::Not(NotExpr { expr: inner_2 })) => unify_impl(inner_1, inner_2, sub),
        (Expr::And(AndExpr { left: left_1, right: right_1 }), Expr::And(AndExpr { left: left_2, right: right_2 })) =>
            unify_impl(left_1, left_2, sub) && unify_impl(right_1, right_2, sub),
        (Expr::Or(OrExpr { left: left_1, right: right_1 }), Expr::Or(OrExpr { left: left_2, right: right_2 })) =>
            unify_impl(left_1, left_2, sub) && unify_impl(right_1, right_2, sub),
        (Expr::Implies(ImpliesExpr { premise: left_1, conclusion: right_1 }), Expr::Implies(ImpliesExpr { premise: left_2, conclusion: right_2 })) =>
            unify_impl(left_1, left_2, sub) && unify_impl(right_1, right_2, sub),
        (Expr::Equiv(EquivExpr { left: left_1, right: right_1 }), Expr::Equiv(EquivExpr { left: left_2, right: right_2 })) =>
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
        Expr::Ref(RefExpr { name }) => match sub.get(name) {
            Some(new_expr) => new_expr.clone(),
            None => expr.clone(),
        },
        Expr::Not(NotExpr { expr }) => Expr::not(apply(sub, expr)),
        Expr::Or(OrExpr { left, right }) => Expr::or(apply(sub, left), apply(sub, right)),
        Expr::And(AndExpr { left, right }) => Expr::and(apply(sub, left), apply(sub, right)),
        Expr::Implies(ImpliesExpr { premise, conclusion }) => Expr::implies(apply(sub, premise), apply(sub, conclusion)),
        Expr::Equiv(EquivExpr { left, right }) => Expr::equiv(apply(sub, left), apply(sub, right)),
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

    pub fn expand(&self, expr: &Expr) -> Vec<Expr> {
        let mut out = Vec::new();
        for rule in &self.rules {
            if let Some(sub) = unify(&rule.pattern, &expr) {
                out.push(apply(&sub, &rule.expr));
            }
        }
        out
    }

    pub fn prove(&mut self, start: &Expr, goal: &Expr) -> Option<Vec<Expr>> {
        let mut parents = HashMap::new();
        let mut frontier = VecDeque::new();
        let mut visited = HashSet::new();
        frontier.push_back(start.clone());
        let mut child = loop {
            let curr = match frontier.pop_front() {
                None => return None,
                Some(node) => node,
            };
            if visited.contains(&curr) {
                continue;
            }
            if curr == *goal {
                break curr;
            }
            for next in self.expand(&curr) {
                parents.insert(next.clone(), curr.clone());
                frontier.push_back(next);
            }
            visited.insert(curr);
        };
        let mut path = vec![ child.clone() ];
        loop {
            let parent = match parents.get(&child) {
                None => break,
                Some(node) => node,
            };
            path.push(parent.clone());
            child = parent.clone();
        }
        path.reverse();
        Some(path)
    }

}

