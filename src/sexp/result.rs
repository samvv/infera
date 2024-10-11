
#[derive(Debug)]
pub enum Error {
    IO(std::io::Error),
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::IO(error) => write!(f, "IO error: {}", error),
        }
    }
}

impl std::error::Error for Error {}

impl From<std::io::Error> for Error {
    fn from(inner: std::io::Error) -> Error {
        Error::IO(inner)
    }
}

pub type Result<T> = std::result::Result<T, Error>;

