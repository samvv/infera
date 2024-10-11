
use infera::sexp;
use infera::fol::{Expr, Parse, Rewriter, Rule, Theorem};

fn main() {
    let file = sexp::parse_file("test.scm").unwrap();
    let thms: Vec<Theorem> = file.elements.iter().map(|x| Theorem::parse(x).unwrap()).collect();
    eprintln!("{:#?}", thms);
    let mut rw = Rewriter::new();
    rw.add_rule(Rule::new(Expr::not(Expr::not(Expr::name("a"))), Expr::name("a")));
    eprintln!("{:#?}", rw.expand(Expr::not(Expr::not(Expr::and(Expr::name("b"), Expr::name("c"))))));
}

