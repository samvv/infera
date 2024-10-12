
#![feature(iterator_try_collect)]

use infera::sexp::{self, Emit};
use infera::fol::{matching_size, AstMeta, Expr, FromSexp, Rewriter, Rule, Theorem, ToSexp, AND_ID, BUILTIN_OPS, EQUIV_ID, IMPLIES_ID};

fn prove(expr: &Expr, rewriter: &mut Rewriter, meta: &AstMeta) -> Option<Vec<Expr>> {
    match expr {
        Expr::PropOp(op) if op.op_id == AND_ID => {
            let mut steps = Vec::new();
            // TODO can be parallelized
            for arg in &op.args {
                // TODO add a small title before proving each arg?
                match prove(&arg, rewriter, meta) {
                    Some(inner_steps) => steps.extend(inner_steps),
                    _ => return None,
                }
            }
            Some(steps)
        }
        Expr::PropOp(op) if op.op_id == EQUIV_ID => {
            let left = op.args.iter().nth(0).unwrap();
            let right = op.args.iter().nth(1).unwrap();
            println!("ℹ️ Going to prove that {} is equivalent to {}", left.to_sexp(meta).emit_string().unwrap(), right.to_sexp(meta).emit_string().unwrap());
            rewriter.prove(left, right)
        },
        _ => unimplemented!(),
    }
}

fn main() -> anyhow::Result<()> {

    eprintln!("Keep an eye on your RAM usage and terminate this application if neccessary!");

    let mut meta = AstMeta::new();
    for op in BUILTIN_OPS.iter() {
        meta.add_op_desc(op.clone());
    }

    let mut rewriter = Rewriter::new(10000);

    rewriter.add_heuristic(1.0, matching_size);

    let kb = sexp::parse_file("kb.scm")?;
    for el in kb.elements {
        let expr = Expr::from_sexp(&el, &mut meta)?;
        match expr {
            Expr::PropOp(p) if p.op_id == EQUIV_ID => {
                let left = p.args.iter().nth(0).unwrap();
                let right = p.args.iter().nth(1).unwrap();
                rewriter.add_rule(Rule::new(left.clone(), right.clone()));
                rewriter.add_rule(Rule::new(right.clone(), left.clone()));
            },
            Expr::PropOp(p) if p.op_id == IMPLIES_ID => {
                let left = p.args.iter().nth(0).unwrap();
                let right = p.args.iter().nth(1).unwrap();
                rewriter.add_rule(Rule::new(left.clone(), right.clone()));
            },
            // TODO process other tautologies too
            _ => {},
        }
    }

    let file = sexp::parse_file("test.scm")?;
    let thms: Vec<Theorem> = file.elements.iter().map(|x| Theorem::from_sexp(x, &mut meta)).try_collect()?;

    // eprintln!("{:#?}", rw.expand(&Expr::not(Expr::not(Expr::and(Expr::name("b"), Expr::name("c"))))));

    for thm in thms {
        println!("⌛ Proving {} ...", meta.resolve_name(thm.name).unwrap());
        match prove(&thm.body, &mut rewriter, &meta) {
            None => println!("❌ Statement could not be proven."),
            Some(steps) => {
                for step in steps {
                    println!("{}", step.to_sexp(&meta).emit_string()?);
                }
                println!("✅ QED");
            }
        }
    }
    Ok(())
}
