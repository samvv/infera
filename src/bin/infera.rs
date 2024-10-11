
use infera::sexp::{self, Emit};
use infera::fol::{AndExpr, EquivExpr, Expr, Parse, Rewriter, Rule, Theorem, ToSexp};

struct Prover {
    rewriter: Rewriter,
}

impl Prover {

    pub fn new(rewriter: Rewriter) -> Self {
        Self {
            rewriter,
        }
    }

    fn prove(&mut self, expr: &Expr) -> Option<Vec<Expr>> {
        match expr {
            Expr::And(AndExpr { left, right }) => {
                // TODO can be parallelized
                match (self.prove(left), self.prove(right)) {
                    (Some(steps_1), Some(steps_2)) => {
                        let mut steps = Vec::new();
                        // TODO add a small title?
                        steps.extend(steps_1);
                        // TODO add a small title?
                        steps.extend(steps_2);
                        Some(steps)
                    },
                    _ => None,
                }
            }
            Expr::Equiv(EquivExpr { left, right }) =>
                self.rewriter.prove(left, right),
            _ => unimplemented!(),
        }
    }

}

fn main() -> anyhow::Result<()> {

    let file = sexp::parse_file("test.scm")?;
    let thms: Vec<Theorem> = file.elements.iter().map(|x| Theorem::parse(x).unwrap()).collect();

    let mut rewriter = Rewriter::new();

    rewriter.add_rule(Rule::new(Expr::not(Expr::not(Expr::name("a"))), Expr::name("a")));

    let mut prover = Prover::new(rewriter);

    // eprintln!("{:#?}", rw.expand(&Expr::not(Expr::not(Expr::and(Expr::name("b"), Expr::name("c"))))));

    for thm in thms {
        let start = Expr::not(Expr::not(Expr::and(Expr::name("b"), Expr::name("c"))));
        let goal = Expr::and(Expr::name("b"), Expr::name("c"));
        println!("Given: {}", start.to_sexp().emit_string()?);
        println!("To prove: {}", goal.to_sexp().emit_string()?);
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
