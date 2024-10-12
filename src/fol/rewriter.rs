use std::collections::{hash_map::Entry, HashMap, HashSet, VecDeque};

use super::{Expr, PropOpExpr, RefExpr};

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
        (Expr::PropOp(p1), Expr::PropOp(p2)) if p1.op_id == p2.op_id => {
            if p1.args.len() != p2.args.len() {
                return false;
            }
            for (a, b) in std::iter::zip(&p1.args, &p2.args) {
                if ! unify_impl(a, b, sub) {
                    return false
                }
            }
            true
        }
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
        Expr::PropOp(p) => Expr::PropOp(PropOpExpr {
            op_id: p.op_id,
            args: p.args.iter().map(|x| apply(sub, x)).collect(),
        }),
    }
}

pub struct Rewriter {
    max_iter: usize,
    rules: Vec<Rule>,
}

impl Rewriter {

    pub fn new(max_iter: usize) -> Self {
        Self {
            max_iter,
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
        visited.insert(start.clone());
        frontier.push_back(start.clone());
        let mut k = 0;
        let mut child = loop {
            if k % 1000 == 0 {
                eprintln!("Starting iteration {}", k);
            }
            if k > self.max_iter {
                // TODO return something more useful
                return None;
            }
            let curr = match frontier.pop_front() {
                None => return None,
                Some(node) => node,
            };
            if curr == *goal {
                break curr;
            }
            for next in self.expand(&curr) {
                if visited.contains(&next) {
                    continue;
                }
                visited.insert(next.clone());
                parents.insert(next.clone(), curr.clone());
                frontier.push_back(next);
            }
            k += 1;
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

