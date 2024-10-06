
pub type Span = std::ops::Range<usize>;

pub trait Spanned { 

    fn span(&self) -> Span;

    fn start_offset(&self) -> usize {
        self.span().start
    }

    fn end_offset(&self) -> usize {
        self.span().end
    }

}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Dot {
    pub span: Span,
}

impl Spanned for Dot {
    fn span(&self) -> Span {
        self.span.clone()
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct LParen {
    pub span: Span,
}

impl LParen {
    pub fn new(span: Span) -> Self {
        Self { span }
    }
}

impl Spanned for LParen {
    fn span(&self) -> Span {
        self.span.clone()
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct LBracket {
    pub span: Span,
}

impl LBracket {
    pub fn new(span: Span) -> Self {
        Self { span }
    }
}

impl Spanned for LBracket {
    fn span(&self) -> Span {
        self.span.clone()
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RParen {
    pub span: Span,
}

impl RParen {
    pub fn new(span: Span) -> Self {
        Self { span }
    }
}

impl Spanned for RParen {
    fn span(&self) -> Span {
        self.span.clone()
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RBracket {
    pub span: Span,
}

impl RBracket {
    pub fn new(span: Span) -> Self {
        Self { span }
    }
}

impl Spanned for RBracket {
    fn span(&self) -> Span {
        self.span.clone()
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Identifier {
    pub text: String,
    pub span: Span,
}

impl Identifier {
    pub fn new(text: String, span: Span) -> Self {
        Self { text, span }
    }
}

impl Spanned for Identifier {
    fn span(&self) -> Span {
        self.span.clone()
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Integer {
    pub value: isize,
    pub span: Span,
}

impl Spanned for Integer {
    fn span(&self) -> Span {
        self.span.clone()
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Token {
    Dot(Dot),
    Integer(Integer),
    Identifier(Identifier),
    LParen(LParen),
    LBracket(LBracket),
    RParen(RParen),
    RBracket(RBracket),
    EndOfFile,
}

impl Spanned for Token {
    fn span(&self) -> Span {
        match self {
            Token::Dot(inner) => inner.span(),
            Token::Integer(inner) => inner.span(),
            Token::Identifier(inner) => inner.span(),
            Token::LParen(inner) => inner.span(),
            Token::RParen(inner) => inner.span(),
            Token::LBracket(inner) => inner.span(),
            Token::RBracket(inner) => inner.span(),
            Token::EndOfFile => panic!("end-of-file token does not have a span"),
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Tail {
    pub dot: Dot,
    pub expr: SExp,
}

impl Spanned for Tail {
    fn span(&self) -> Span {
        self.dot.start_offset() .. self.expr.end_offset()
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum SExp {
    List {
        open_delim: Token,
        elements: Vec<SExp>,
        tail: Option<Box<Tail>>,
        close_delim: Token,
    },
    Identifier(Identifier),
    Integer(Integer),
}

impl Spanned for SExp {
    fn span(&self) -> Span {
        match self {
            SExp::List { open_delim, close_delim, .. } => open_delim.start_offset()..close_delim.end_offset(),
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
    fn span(&self) -> Span {
        0..self.end_offset
    }
}

