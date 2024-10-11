
use std::collections::VecDeque;

use super::result::Result;
use super::cst::*;
use super::scanner::Scanner;

pub struct Parser<C> {
    token_buffer: VecDeque<Token>,
    scanner: Scanner<C>,
}

impl <C: Iterator<Item = Result<char>>> Parser<C> {

    pub fn new(scanner: Scanner<C>) -> Self {
        Self { scanner, token_buffer: VecDeque::new() }
    }

    fn peek_token(&mut self) -> Result<Token> {
        match self.token_buffer.front() {
            Some(token) => Ok(token.clone()),
            None => {
                let t0 = self.scanner.scan()?;
                self.token_buffer.push_back(t0.clone());
                Ok(t0)
            }
        }
    }

    fn get_token(&mut self) -> Result<Token> {
        match self.token_buffer.pop_front() {
            Some(token) => Ok(token),
            None => self.scanner.scan(),
        }
    }

    pub fn parse_sexp(&mut self) -> Result<SExp> {
        let mut stack = VecDeque::new();

        macro_rules! element {
            ($value: expr) => {
                match stack.back_mut() {
                    None => return Ok($value),
                    Some((_open_delim, elements, _tail)) => {
                        elements.push($value);
                    }
                }
            }
        }

        loop {
            let t0 = self.get_token()?;
            match t0 {
                Token::LParen(..) => {
                    let new_elements = Vec::new();
                    stack.push_back((t0, new_elements, None));
                }
                Token::Identifier(name) => {
                    element!(SExp::Identifier(name));
                }
                Token::Integer(int) => {
                    element!(SExp::Integer(int));
                }
                Token::Dot(dot) => {
                    match stack.back_mut() {
                        Some((_open_delim, _elements, tail @ None)) => {
                            *tail = Some(Box::new(Tail { dot, expr: self.parse_sexp()? }));
                        },
                        _ => todo!(), // Error
                    }
                },
                Token::RParen(..) => {
                    match stack.pop_back() {
                        Some((open_delim, elements, tail)) => {
                            element!(SExp::List(List { open_delim, elements, tail, close_delim: t0 }));
                        },
                        None => todo!(), // Error
                    }
                }
                _ => todo!(),
            }
        }
    }

    pub fn parse_file(&mut self) -> Result<SFile> {
        let mut elements = Vec::new();
        let end_offset;
        loop {
            let t0 = self.peek_token()?;
            if let Token::EndOfFile = t0 {
                end_offset = self.scanner.offset;
                break;
            }
            elements.push(self.parse_sexp()?);
        }
        Ok(SFile { elements, end_offset })
    }

}

#[cfg(test)]
mod test {

    use super::super::scanner::Scanner;
    use super::super::cst::*;
    use super::Parser;

    #[test]
    fn test_parse_list_ids() {
        let scanner = Scanner::new("(foo baz bar)".chars().map(|el| Ok(el)));
        let mut parser = Parser::new(scanner);
        let e0 = parser.parse_sexp().unwrap();
        let SExp::List(List { open_delim, elements, tail, close_delim }) = e0 else {
            panic!("not a sexp list");
        };
        assert_eq!(open_delim, Token::LParen(LParen { span: 0..1 }));
        assert_eq!(elements[0], SExp::Identifier(Identifier { text: "foo".to_string(), span: 1..4 }));
        assert_eq!(elements[1], SExp::Identifier(Identifier { text: "baz".to_string(), span: 5..8 }));
        assert_eq!(elements[2], SExp::Identifier(Identifier { text: "bar".to_string(), span: 9..12 }));
        assert_eq!(tail, None);
        assert_eq!(close_delim, Token::RParen(RParen { span: 12..13 }));
    }

    #[test]
    fn test_parse_symbol() {
        let scanner = Scanner::new("foo".chars().map(|el| Ok(el)));
        let mut parser = Parser::new(scanner);
        let e0 = parser.parse_sexp().unwrap();
        assert_eq!(e0, SExp::Identifier(Identifier { text: "foo".to_string(), span: 0..3 }));
    }

    #[test]
    fn test_parse_integer() {
        let scanner = Scanner::new("1234".chars().map(|el| Ok(el)));
        let mut parser = Parser::new(scanner);
        let e0 = parser.parse_sexp().unwrap();
        assert_eq!(e0, SExp::Integer(Integer { value: 1234, span: 0..4 }));
    }

}
