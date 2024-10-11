
pub type Span = std::ops::Range<usize>;

pub trait Spanned {

    fn span(&self) -> Option<Span>;

    fn start_offset(&self) -> usize {
        self.span().unwrap().start
    }

    fn end_offset(&self) -> usize {
        self.span().unwrap().end
    }

}

macro_rules! define_tokens {
    ($($name:ident { $($field_name:ident: $field_ty:ty )* } ),* $(,)?) => {
        $(
            #[derive(Clone, Debug, PartialEq, Eq)]
            pub struct $name {
                pub span: Option<Span>,
                $(pub $field_name: $field_ty),*
            }
            impl $name {
                pub fn with_span(span: Span $(, $field_name: $field_ty)*) -> Self {
                    Self { span: Some(span) $(, $field_name )* }
                }
                pub fn new($($field_name: $field_ty),*) -> Self {
                    Self { span: None $(, $field_name )* }
                }
            }
            impl Spanned for $name {
                fn span(&self) -> Option<Span> {
                    self.span.clone()
                }
            }
        )*
        #[derive(Clone, Debug, PartialEq, Eq)]
        pub enum Token {
            $($name($name)),*
        }
        impl Spanned for Token {
            fn span(&self) -> Option<Span> {
                match self {
                    $(Self::$name(inner) => inner.span(),)*
                    }
                }
            }
        }
}

define_tokens!(
    EndOfFile {},
    Dot {},
    LParen {},
    RParen {},
    LBracket {},
    RBracket {},
    Identifier { text: String },
    Integer { value: i64 },
);

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Tail {
    pub dot: Dot,
    pub expr: SExp,
}

impl Spanned for Tail {
    fn span(&self) -> Option<Span> {
        Some(self.dot.start_offset() .. self.expr.end_offset())
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct List {
    pub open_delim: Token,
    pub elements: Vec<SExp>,
    pub tail: Option<Box<Tail>>,
    pub close_delim: Token,
}

impl List {

    pub fn get(&self, count: usize) -> ParseResult<&SExp> {
        match self.elements.iter().nth(count) {
            None => Err(ParseError::Index(count)),
            Some(element) => Ok(element),
        }
    }

}

#[derive(Copy, Clone, Debug, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub enum Expected {
    List,
    Identifier,
    Integer,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum SExp {
    List(List),
    Identifier(Identifier),
    Integer(Integer),
}

#[derive(Debug)]
pub enum ParseError {
    /// Returned when an S-expression was of the wrong kind.
    Type(Expected),
    /// Returned when an offset was out of range.
    Index(usize),
    /// Returned when a specific keyword was expected
    Keyword(String, String),
}

impl std::fmt::Display for ParseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        todo!()
    }
}

impl std::error::Error for ParseError {}

type ParseResult<T> = std::result::Result<T, ParseError>;

impl SExp {

    pub fn list(elements: &[SExp]) -> Self {
        SExp::List(List {
            open_delim: Token::LParen(LParen::new()),
            elements: elements.to_vec(),
            tail: None,
            close_delim: Token::RParen(RParen::new()),
        })
    }

    pub fn ident<S: Into<String>>(s: S) -> Self {
        SExp::Identifier(Identifier::new(s.into()))
    }

    pub fn as_list(&self) -> ParseResult<&List> {
        match self {
            SExp::List(inner) => Ok(inner),
            _ => Err(ParseError::Type(Expected::List)),
        }
    }

    pub fn as_identifier(&self) -> ParseResult<&Identifier> {
        match self {
            SExp::Identifier(inner) => Ok(inner),
            _ => Err(ParseError::Type(Expected::Integer)),
        }
    }

    pub fn as_integer(&self) -> ParseResult<&Integer> {
        match self {
            SExp::Integer(inner) => Ok(inner),
            _ => Err(ParseError::Type(Expected::Integer)),
        }
    }

    pub fn as_keyword<S: AsRef<str>>(&self, str: S) -> ParseResult<&Identifier> {
        let name = self.as_identifier()?;
        if name.text != str.as_ref() {
            return Err(ParseError::Keyword(name.text.clone(), "defthm".to_string()));
        }
        Ok(name)
    }

}

impl Spanned for SExp {
    fn span(&self) -> Option<Span> {
        match self {
            SExp::List(List { open_delim, close_delim, .. }) => Some(open_delim.start_offset()..close_delim.end_offset()),
            SExp::Identifier(name) => name.span(),
            SExp::Integer(int) => int.span(),
        }
    }
}

#[derive(Clone, Debug)]
pub struct SFile {
    pub elements: Vec<SExp>,
    pub end_offset: usize,
}

impl Spanned for SFile {
    fn span(&self) -> Option<Span> {
        Some(0..self.end_offset)
    }
}

