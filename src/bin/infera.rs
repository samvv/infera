
use core::panic;
use std::collections::HashMap;

use infera::sexp::{self, Emit};
use infera::fol::{Expr, OpDesc, Parser, PropOpExpr, Rewriter, Rule, Theorem, ToSexp, AND_TABLE, BUILTIN_OPS, EQUIV_TABLE};

struct Prover {
    rewriter: Rewriter,
    ops: HashMap<usize, OpDesc>,
}

impl Prover {

    pub fn new(rewriter: Rewriter, ops: &[OpDesc]) -> Self {
        let m = ops.iter().map(|o| (o.id, o.clone())).collect();
        Self {
            rewriter,
            ops: m,
        }
    }

    fn is_and_op(&self, op: &PropOpExpr) -> bool {
        self.ops.get(&op.op_id).unwrap().table == *AND_TABLE
    }

    fn is_equiv_op(&self, op: &PropOpExpr) -> bool {
        self.ops.get(&op.op_id).unwrap().table == *EQUIV_TABLE
    }

    fn prove(&mut self, expr: &Expr) -> Option<Vec<Expr>> {
        match expr {
            Expr::PropOp(op) if self.is_and_op(op) => {
                let mut steps = Vec::new();
                // TODO can be parallelized
                for arg in &op.args {
                    // TODO add a small title before proving each arg?
                    match self.prove(&arg) {
                        Some(inner_steps) => steps.extend(inner_steps),
                        _ => return None,
                    }
                }
                Some(steps)
            }
            Expr::PropOp(op) if self.is_equiv_op(op) => {
                let left = op.args.iter().nth(0).unwrap();
                let right = op.args.iter().nth(1).unwrap();
                println!("Going to prove that {} is equivalent to {}", left.to_sexp().emit_string().unwrap(), right.to_sexp().emit_string().unwrap());
                self.rewriter.prove(left, right)
            },
            _ => unimplemented!(),
        }
    }

}

fn main() -> anyhow::Result<()> {

    let mut ops = BUILTIN_OPS.clone();
    let mut parser = Parser::with_ops(&ops);

    let mut rewriter = Rewriter::new();

    let kb = sexp::parse_file("kb.scm")?;
    for el in kb.elements {
        let l = el.as_list().unwrap();
        match l.get(0)?.as_identifier()?.text.as_str() {
            "equiv" => {
                let left = parser.parse_expr(l.get(1)?)?;
                let right = parser.parse_expr(l.get(2)?)?;
                rewriter.add_rule(Rule::new(left.clone(), right.clone()));
                rewriter.add_rule(Rule::new(right, left));
            },
            "implies" => {
                let left = parser.parse_expr(l.get(1)?)?;
                let right = parser.parse_expr(l.get(2)?)?;
                rewriter.add_rule(Rule::new(left, right));
            },
            _ => panic!("invalid data in kb.scm"),
        }
    }

    let file = sexp::parse_file("test.scm")?;
    let thms: Vec<Theorem> = file.elements.iter().map(|x| parser.parse_theorem(x).unwrap()).collect();

    let mut prover = Prover::new(rewriter, &ops);

    // eprintln!("{:#?}", rw.expand(&Expr::not(Expr::not(Expr::and(Expr::name("b"), Expr::name("c"))))));

    for thm in thms {
        println!("Proving {} ...", thm.name);
        match prover.prove(&thm.body) {
            None => println!("Statement could not be proven."),
            Some(steps) => {
                for step in steps {
                    println!("{}", step.to_sexp().emit_string()?);
                }
                println!("QED");
            }
        }
    }
    Ok(())
}
