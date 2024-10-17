
use std::collections::VecDeque;

use super::cst::*;
use super::result::Result;
use super::cst::Token;

const EOF: char = '\u{FFFF}';

fn is_whitespace(ch: char) -> bool {
    matches!(ch, '\n' | '\r' | '\t' | ' ')
}

pub struct Scanner<C> {
    chars: C,
    pub offset: usize,
    char_buffer: VecDeque<char>,
}

pub struct OkIter<T: Iterator> { 
    iter: T,
}

impl <I: Iterator> OkIter<I> {

    pub fn new(iter: I) -> Self {
        Self { iter }
    }

}

impl <I: Iterator> Iterator for OkIter<I> {

    type Item = Result<I::Item>;

    fn next(&mut self) -> Option<Self::Item> {
        match self.iter.next() {
            None => None,
            Some(value) => Some(Ok(value)),
        }
    }

}

impl <'a> Scanner<std::iter::Map<std::str::Chars<'a>, fn (el: char) -> Result<char>>> {
    pub fn from_str(s: &'a str) -> Self {
        Self::new(s.chars().map(|element| Ok(element)))
    }
}

impl <C: Iterator<Item = Result<char>>> Scanner<C> {

    pub fn new(chars: C) -> Self {
        Self {
            chars,
            offset: 0,
            char_buffer: VecDeque::new(),
        }
    }

    fn read_char(&mut self) -> Result<char> {
        match self.chars.next() {
            None => Ok(EOF),
            Some(result) => result,
        }
    }

    fn get_char(&mut self) -> Result<char> {
        let ch = match self.char_buffer.pop_front() {
            Some(ch) => ch,
            None => self.read_char()?,
        };
        self.offset += 1;
        Ok(ch)
    }

    fn peek_char(&mut self) -> Result<char> {
        match self.char_buffer.front() {
            Some(ch) => Ok(*ch),
            None => {
                let ch = self.read_char()?;
                self.char_buffer.push_back(ch);
                Ok(ch)
            }
        }
    }

    pub fn scan(&mut self) -> Result<Token> {

        let mut c0;
        let mut start_offset;

        loop {
            start_offset = self.offset;
            c0 = self.get_char()?;
            if c0 == ';' {
                loop {
                    let c1 = self.get_char()?;
                    if c1 == '\n' || c1 == EOF {
                        break;
                    }
                }
                continue;
            }
            if is_whitespace(c0) {
                continue;
            }
            break;
        }

        match c0 {

            EOF => return Ok(Token::EndOfFile(EndOfFile::new())),

            '(' => return Ok(Token::LParen(LParen::with_span(start_offset..self.offset))),
            ')' => return Ok(Token::RParen(RParen::with_span(start_offset..self.offset))),
            '[' => return Ok(Token::LBracket(LBracket::with_span(start_offset..self.offset))),
            ']' => return Ok(Token::RBracket(RBracket::with_span(start_offset..self.offset))),

            '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' => {
                let mut value = c0.to_digit(10).unwrap() as i64;
                loop {
                    let c1 = self.peek_char()?;
                    if !c1.is_ascii_digit() {
                        break;
                    }
                    self.get_char()?;
                    value = value * 10 + c1.to_digit(10).unwrap() as i64;
                }
                return Ok(Token::Integer(Integer::with_span(start_offset..self.offset, value)))
            }

            'a' | 'b' | 'c' | 'd' | 'e' | 'f' | 'g' | 'h'
                | 'i' | 'j' | 'k' | 'l' | 'm' | 'n' | 'o'
                | 'p' | 'q' | 'r' | 's' | 't' | 'u' | 'v'
                | 'w' | 'x' | 'y' | 'z' | 'A' | 'B' | 'C'
                | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J'
                | 'K' | 'L' | 'M' | 'N' | 'O' | 'P' | 'Q'
                | 'R' | 'S' | 'T' | 'U' | 'V' | 'W' | 'X'
                | 'Y' | 'Z' | '_' | '+' | '-' | '*' | '/'
                | '^' | '&' | '|' | '%' | '$' | '?'
                | '!' | '<' | '>' | '=' | '~'
            => {
                let mut text = String::new();
                text.push(c0);
                loop {
                    let c1 = self.peek_char()?;
                    if !matches!(c1, 'a' | 'b' | 'c' | 'd' | 'e' | 'f' | 'g' | 'h'
                                         | 'i' | 'j' | 'k' | 'l' | 'm' | 'n' | 'o'
                                         | 'p' | 'q' | 'r' | 's' | 't' | 'u' | 'v'
                                         | 'w' | 'x' | 'y' | 'z' | 'A' | 'B' | 'C'
                                         | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J'
                                         | 'K' | 'L' | 'M' | 'N' | 'O' | 'P' | 'Q'
                                         | 'R' | 'S' | 'T' | 'U' | 'V' | 'W' | 'X'
                                         | 'Y' | 'Z' | '0' | '1' | '2' | '3' | '4'
                                         | '5' | '6' | '7' | '8' | '9' | '_' | '+'
                                         | '-' | '*' | '/' | '^' | '&' | '|' | '%'
                                         | '$' | '?' | '!' | '<' | '>' | '=' | '~') {
                        break;
                    }
                    self.get_char()?;
                    text.push(c1);
                }
                return Ok(Token::Identifier(Identifier::with_span(start_offset..self.offset, text)));
            }

            _ => todo!(),

        }

    }

}

#[cfg(test)]
mod test {

    use super::super::cst::*;
    use super::Scanner;

    #[test]
    fn test_scan_identifier() {
        let mut scanner = Scanner::from_str("foo");
        let t0 = scanner.scan().unwrap();
        assert_eq!(t0, Token::Identifier(Identifier { text: "foo".to_string(), span: Some(0..3) }));
    }

}
