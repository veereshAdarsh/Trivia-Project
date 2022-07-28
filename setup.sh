dropdb trivia;
dropdb trivia_test;
Get-Content backend/trivia.psql | psql -U postgres trivia;
psql -U postgres trivia
\dt
SELECT * FROM categories;
SELECT * FROM questions;
\q