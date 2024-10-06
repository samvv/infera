
#[derive(Debug)]
pub enum Error {
    IO(std::io::Error),
}

impl From<std::io::Error> for Error {
    fn from(inner: std::io::Error) -> Error {
        Error::IO(inner)
    }
}

pub type Result<T> = std::result::Result<T, Error>;

