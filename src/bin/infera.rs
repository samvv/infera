
use infera::sexp;
use infera::fol::{Parse, Theorem};

fn main() {
    let file = sexp::parse_file("test.scm").unwrap();
    let thms: Vec<Theorem> = file.elements.iter().map(|x| Theorem::parse(x).unwrap()).collect();
    eprintln!("{:#?}", thms);
}

