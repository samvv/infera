use std::{fmt::Formatter, io::{Cursor, Read}};

use super::{Identifier, Integer, List, Sexp};


pub trait Emit {

    fn emit<W: std::io::Write>(&self, w: &mut W) -> std::io::Result<()>;

    fn emit_string(&self) -> std::io::Result<String> {
        let mut buf = Vec::new();
        self.emit(&mut buf)?;
        Ok(String::from_utf8(buf).unwrap())
    }
}

impl Emit for Sexp {
    fn emit<W: std::io::Write>(&self, w: &mut W) -> std::io::Result<()> {
        match self {
            Self::Integer(int) => int.emit(w),
            Self::Identifier(name) => name.emit(w),
            Self::List(l) => l.emit(w),
        }
    }
}

impl Emit for Integer {
    fn emit<W: std::io::Write>(&self, w: &mut W) -> std::io::Result<()> {
        write!(w, "{}", self.value)
    }
}

impl Emit for Identifier {
    fn emit<W: std::io::Write>(&self, w: &mut W) -> std::io::Result<()> {
        write!(w, "{}", self.text)
    }
}

impl Emit for List {
    fn emit<W: std::io::Write>(&self, w: &mut W) -> std::io::Result<()> {
        write!(w, "(")?;
        let mut iter = self.elements.iter();
        if let Some(el) = iter.next() {
            el.emit(w)?;
            for element in iter {
                write!(w, " ")?;
                element.emit(w)?;
            }
        }
        if let Some(tail) = &self.tail {
            write!(w, " . ")?;
            tail.expr.emit(w)?;
        }
        write!(w, ")")?;
        Ok(())
    }
}
