
use infera::sexp;

fn main() {
    eprintln!("{:?}", sexp::parse_file("test.scm"));
}

