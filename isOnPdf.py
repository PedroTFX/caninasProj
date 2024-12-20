import PyPDF2
import os

def make_txt_from_pdf(file_path):
    filename = file_path.split('/')[-1]
    if filename.endswith('.txt'):
        return
        
    filename = filename.split('.')[0]
    with open(file_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        with open( filename + '.txt', 'w') as text_file:
            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]
                text_file.write(page.extract_text())
    print('Text file created successfully!')
    
def find_terms_in_text(text, terms):
    for term in terms:
        if term.lower() in text.lower():
            print(f'Found term: {term}')
            

def get_all_txt_files():
    return [f for f in os.listdir('.') if f.endswith('.txt')]

# Example usage:
file_path = 'UndercoverMartyn.pdf'  # Replace with the path to your PDF file
frequentist_terms = [
    "P-value", "Null hypothesis", "Alternative hypothesis", "Confidence interval",
    "Significance level", "Type I error", "Type II error", "Test statistic",
    "Maximum likelihood estimation", "Standard error", "Sampling distribution",
    "Hypothesis testing", "t-test", "ANOVA", "Chi-squared test", "Degrees of freedom",
    "Reject null hypothesis", "Fail to reject null hypothesis", "Critical value",
    "Error rates", "95% confidence interval"
]

# Bayesian Terminologies
bayesian_terms = [
    "Prior distribution", "Posterior distribution", "Likelihood", "Bayes’ theorem",
    "Credible interval", "Bayesian updating", "Markov Chain Monte Carlo",
    "Posterior predictive distribution", "Variational inference", "Conjugate priors",
    "Non-informative prior", "Hierarchical model", "Marginal likelihood",
    "Bayes factor", "Updating beliefs", "Posterior probability", "Incorporating priors",
    "Posterior predictive checks", "of"
]

file_path = 'UndercoverMartyn.pdf'  # Replace with the path to your PDF file


make_txt_from_pdf(file_path)
txt_files = get_all_txt_files()
for txt_file in txt_files:
    print(f'Analyzing file: {txt_file}')
    
    find_terms_in_text(txt_file, frequentist_terms)
    find_terms_in_text(txt_file, bayesian_terms)

# find_terms_in_text('text.txt', bayesian_terms)


