
mod result;
mod cst;
mod scanner;
mod parser;

use std::path::Path;

pub use result::*;
pub use cst::*;
pub use scanner::*;
pub use parser::*;

pub fn parse_file<P: AsRef<Path>>(filepath: P) -> Result<SFile> {
    let text = std::fs::read_to_string(filepath.as_ref())?;
    let scanner = Scanner::new(text.chars().map(|element| Ok(element)));
    let mut parser = Parser::new(scanner);
    parser.parse_file()
}

