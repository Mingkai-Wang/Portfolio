library(ggplot2)
library(dplyr)
library(tidyr)
library(tidyverse)
library(caret)
library(stats)
df <- read.csv("~/Desktop/Term 1/6003 Analytics Strategy/Graded Team Assignment - Gender Discrimination Lawsuit/Lawsuit.csv")

head(df)
str(df)
summary(df)


# Check for missing values
colSums(is.na(df))

# Correlation matrix
cor_matrix <- cor(df)
print(cor_matrix)

# Group by Dept, Rank, and Gender
grouped_data <- df %>%
  group_by(Dept, Rank, Gender) %>%
  summarise(Count = n())

# View the grouped data
print(grouped_data)


# Visualizations

# Histogram of Salary
ggplot(df, aes(x = Sal95)) +
  geom_histogram(bins = 30, fill = "blue", alpha = 0.7) +
  labs(title = "Distribution of Salary (1995)", x = "Salary", y = "Count")

# Scatter plot of Experience vs Salary
ggplot(df, aes(x = Exper, y = Sal95)) +
  geom_point() +
  geom_smooth(method = "lm", se = FALSE, color = "red") +
  labs(title = "Experience vs Salary", x = "Years of Experience", y = "Salary (1995)")

# Box plot of Salary by Gender
ggplot(df, aes(x = factor(Gender), y = Sal95, fill = factor(Gender))) +
  geom_boxplot() +
  labs(title = "Salary Distribution by Gender", x = "Gender", y = "Salary (1995)")

# Split data into training and testing sets
set.seed(123)
train_index <- createDataPartition(df$Sal95, p = 0.8, list = FALSE)
train_data <- df[train_index, ]
test_data <- df[-train_index, ]

# Linear Regression
lm_model <- lm(Sal95 ~ Exper + Gender + Rank, data = train_data)
summary(lm_model)

# Predict on test data
lm_predictions <- predict(lm_model, newdata = test_data)

# Calculate Mean Squared Error
mse <- mean((test_data$Sal95 - lm_predictions)^2)
print(paste("Mean Squared Error:", mse))

# Logistic Regression (predicting if salary is above median)
median_salary <- median(df$Sal95)
df$high_salary <- as.factor(ifelse(df$Sal95 > median_salary, 1, 0))

logistic_model <- glm(high_salary ~ Exper + Gender + Rank, data = train_data, family = "binomial")
summary(logistic_model)

# Predict on test data
logistic_predictions <- predict(logistic_model, newdata = test_data, type = "response")
logistic_predictions_class <- ifelse(logistic_predictions > 0.5, 1, 0)

# Calculate accuracy
accuracy <- mean(logistic_predictions_class == test_data$high_salary)
print(paste("Logistic Regression Accuracy:", accuracy))

# Additional statistical tests

# T-test for salary difference between genders
t_test_result <- t.test(Sal95 ~ Gender, data = df)
print(t_test_result)

# ANOVA for salary differences among ranks
anova_result <- aov(Sal95 ~ factor(Rank), data = df)
summary(anova_result)

# Convert multiple columns to factors
df$Gender <- as.factor(df$Gender)
df$Clin <- as.factor(df$Clin)
df$Cert <- as.factor(df$Cert)