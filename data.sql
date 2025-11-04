CREATE DATABASE loan_db;

USE loan_db;

CREATE TABLE loan_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    income FLOAT,
    loan_amount FLOAT,
    credit_history INT,
    prediction VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
SELECT * FROM loan_predictions;
