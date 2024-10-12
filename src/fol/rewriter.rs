use core::f32;
use std::{cmp::Ordering, collections::{hash_map::Entry, BinaryHeap, HashMap, HashSet, VecDeque}};

use super::{Expr, Name, PropOpExpr, RefExpr};

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

type Subst = HashMap<Name, Expr>;

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

pub trait Heuristic = Fn(&Expr, &Expr) -> f32;

fn sigmoid(x: f32) -> f32 {
    let p = f32::powf(f32::consts::E, x);
    p / (1.0 + p)
}

pub fn matching_size(start: &Expr, goal: &Expr) -> f32 {
    let x = start.len() as f32 / goal.len() as f32;
    2.0 * (sigmoid(x) - 0.5)
}

pub struct Rewriter<'a> {
    heuristics: Vec<(f32, Box<dyn Heuristic + 'a>)>,
    max_iter: usize,
    rules: Vec<Rule>,
}

struct Edge {
    cost: f32,
    expr: Expr,
}

impl Edge {

    fn new(expr: Expr, cost: f32) -> Self {
        Self {
            expr,
            cost,
        }
    }

}

const EPSILON: f32 = 0.000001; // Taken from glMatrix

fn approx_eq(a: f32, b: f32) -> bool {
    return (a - b).abs() <= EPSILON * f32::max(1.0, f32::max(a.abs(), b.abs())); // Taken from glMatrix
}

impl PartialEq for Edge {
    fn eq(&self, other: &Self) -> bool {
        approx_eq(self.cost, other.cost) && self.expr.eq(&other.expr)
    }
}

impl Eq for Edge {}

impl Ord for Edge {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        if approx_eq(self.cost, other.cost) {
            self.expr.cmp(&other.expr)
        } else if self.cost < other.cost {
            Ordering::Less
        } else {
            Ordering::Greater
        }
    }
}

impl PartialOrd for Edge {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

impl <'a> Rewriter<'a> {

    pub fn new(max_iter: usize) -> Self {
        Self {
            max_iter,
            heuristics: Vec::new(),
            rules: Vec::new(),
        }
    }

    pub fn add_heuristic<H: Heuristic + 'a>(&mut self, weight: f32, heuristic: H) {
        self.heuristics.push((weight, Box::new(heuristic)));
    }

    pub fn add_rule(&mut self, rule: Rule) {
        self.rules.push(rule);
    }

    pub fn expand_unify(&self, expr: &Expr) -> Vec<Expr> {
        let mut out = Vec::new();
        for rule in &self.rules {
            if let Some(sub) = unify(&rule.pattern, &expr) {
                out.push(apply(&sub, &rule.expr));
            }
        }
        out
    }

    pub fn expand_visit(&self, expr: &Expr) -> Vec<Expr> {
        let mut out = Vec::new();
        out.extend(self.expand_unify(expr));
        match expr {
            Expr::Ref(..) => {},
            Expr::PropOp(op) => {
                for (i, arg) in op.args.iter().enumerate() {
                    for new_arg in self.expand_visit(&arg) {
                        let mut new_args: Vec<_> = op.args.iter().take(i).cloned().collect();
                        new_args.push(new_arg);
                        new_args.extend(op.args.iter().skip(i+1).cloned());
                        out.push(Expr::PropOp(PropOpExpr {
                            op_id: op.op_id,
                            args: new_args,
                        }));
                    }
                }
            }
        }
        out
    }

    pub fn expand(&self, expr: &Expr) -> Vec<Expr> {
        self.expand_visit(expr)
    }

    pub fn estimate(&self, a: &Expr, b: &Expr) -> f32 {
        let mut res = 0.0;
        let mut weights = 0.0;
        for (w, h) in &self.heuristics {
            weights += w;
            res += w * h(a, b);
        }
        res / weights
    }

    pub fn prove(&mut self, start: &Expr, goal: &Expr) -> Option<Vec<Expr>> {
        let mut parents = HashMap::new();
        let mut frontier = BinaryHeap::new();
        let mut visited = HashSet::new();
        visited.insert(start.clone());
        frontier.push(Edge::new(start.clone(), 0.0));
        let mut k = 0;
        let mut child = loop {
            // eprintln!("Iter {}", k);
            if k % 1000 == 0 {
                eprintln!("Starting iteration {}", k);
            }
            if k > self.max_iter {
                // TODO return something more useful
                return None;
            }
            let curr = match frontier.pop() {
                None => return None,
                Some(edge) => edge.expr,
            };
            if curr == *goal {
                break curr;
            }
            for expr in self.expand(&curr) {
                if visited.contains(&expr) {
                    continue;
                }
                let cost = self.estimate(&curr, &expr);
                // eprintln!("Cost = {}, len = {}, orig len = {}", cost, expr.len(), curr.len());
                // eprintln!("{:?}", expr);
                visited.insert(expr.clone());
                parents.insert(expr.clone(), curr.clone());
                frontier.push(Edge::new(expr, cost));
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

