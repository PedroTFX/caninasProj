import PyPDF2
import re
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
    
# make a dictionary of terms and their frequency
def find_terms_in_text(text, terms):
    lines = re.split(r'[.\n,]', text)
    term_freq = {}
    
    for term, synonyms in terms.items():
        term_freq[term] = 0
        for synonym in synonyms:
            for line in lines:
                if synonym.lower() in line.lower():
                    term_freq[term] += 1
                
    if term_freq:
        print('---------------Terms Stats-----------------------')
    print(term_freq if term_freq else 'No terms found')
    return term_freq
            

def get_all_txt_files():
    return [f for f in os.listdir('.') if f.endswith('.txt')]

# Example usage:
# file_path = 'bennett2020.pdf'  # Replace with the path to your PDF file
frequentist_terms = {
    "P-value": [
        "p-value", "significance probability", "test probability", "𝑝<0.05", "p<0.05"
    ],
    "Null hypothesis": [
        "null hypothesis", "hypothesis of no effect", "H₀",  "reject the null hypothesis"
    ],
    "Alternative hypothesis": [
        "alternative hypothesis", "H₁", "hypothesis of an effect"
    ],
    "Test statistic": [
        "test statistic", "observed statistic", "t-statistic", "z-statistic", "F-statistic", "chi-square statistic", "𝜒2", "χ2", "chi-square"
    ],
    "F-test": [
        "f-test", "ANOVA test", "analysis of variance test"
    ],
    "T-test": [
        "t-test", "student's t-test", "independent t-test", "paired t-test", "Student's 𝑡", "Pearson\'s correlation", "𝑡"
    ],
    "Maximum likelihood estimation (MLE)": [
        "maximum likelihood estimation", "likelihood estimation", "likelihood-based method"
    ],
    "Confidence interval (CI)": [
        "confidence interval", "interval estimate", "precision interval", "range of estimates"
    ],
    "Standard error (SE)": [
        "standard error", "estimated error", "standard deviation of the sample mean"
    ],
    "Type I error (false positive)": [
        "type I error", "alpha error", "false rejection"
    ],
    "Type II error (false negative)": [
        "type II error", "beta error", "false acceptance"
    ],
    "Linear regression": [
        "linear regression", "ordinary least squares", "OLS", "linear least squares"
    ],
    "Logistic regression": [
        "logistic regression", "binary regression", "log-odds model"
    ],
    "Generalized linear model (GLM)": [
        "generalized linear model", "GLM", "generalized linear model with Poisson", "GLM with binomial"
    ],
    "Residual analysis": [
        "residual analysis", "error analysis", "fit residuals"
    ],
    "Parametric test": [
        "parametric test", "test based on assumptions", "homoscedasticity"
    ],
    "Non-parametric test": [
        "non-parametric test", "distribution-free test", "rank-based test", "Mann-Whitney U test" " 𝑈", "Kruskal-Wallis"
    ],
    "Likelihood function": [
        "likelihood model", "data likelihood"
    ],
    "Analysis of variance": [
        "Analysis of variance", "AMOVA","ANCOVA","ANOVA","MANOVA"
    ]
}

# Bayesian Terminologies and Synonyms
bayesian_terms = {
    "Bayes_Theorem": [
        "Bayesian formula",
        "Bayes rule",
        "Conditional probability update",
        "Posterior probability formula",
        "Bayesian updating",
        "Inverse probability",
        "Bayes' law"
    ],
    "Prior_Distribution": [
        "Prior belief",
        "Initial probability distribution",
        "Pre-data distribution",
        "Prior assumption",
        "Subjective probability",
        "Initial estimate",
        "Prior probability density",
        "Non-informative prior",
        "Weakly informative prior"
    ],
    "Posterior_Distribution": [
        "Updated belief distribution",
        "Post-data probability",
        "Final probability distribution",
        "Conditional probability (after observing data)",
        "Bayesian posterior",
        "Updated probability density"
    ],
    "Likelihood": [
        "Data probability",
        "Evidence probability",
        "Likelihood function",
        "Fit of the data to the model",
        "Probability of the observed data",
        "Data-generating probability",
        "Model likelihood"
    ],
    "Inference": [
        "Bayesian inference",
        "Probabilistic reasoning",
        "Statistical estimation",
        "Parameter estimation",
        "Probabilistic model estimation",
        "Deductive learning",
        "Posterior inference"
    ],
    "Markov_Chain_Monte_Carlo": [
        "MCMC methods",
        "Bayesian sampling methods",
        "Stochastic simulation",
        "Random walk Monte Carlo",
        "Gibbs sampling",
        "Metropolis-Hastings algorithm",
        "Hamiltonian Monte Carlo",
        "MCMC convergence analysis",
        "Bayesian computational algorithms"
    ],
    "Conjugate_Priors": [
        "Analytical priors",
        "Simplifying priors",
        "Conjugate families of distributions",
        "Prior-posterior matching",
        "Natural conjugate priors",
        "Closed-form posterior priors"
    ],
    "Hierarchical_Models": [
        "Bayesian hierarchical modeling",
        "Multilevel Bayesian models",
        "Nested Bayesian models",
        "Random-effects Bayesian models",
        "Partial pooling models",
        "Hierarchical Bayesian analysis"
    ],
    "Credible_Interval": [
        "Bayesian interval",
        "Posterior interval",
        "Probability interval",
        "Confidence-like interval",
        "Bayesian range",
        "Credible probability bounds"
    ],
    "Posterior_Predictive_Check": [
        "Bayesian model diagnostics",
        "Posterior predictive simulation",
        "Model adequacy check",
        "Predictive posterior assessment",
        "Simulation-based diagnostics",
        "Model fit evaluation"
    ],
    "General_Bayesian_Concepts": [
        "Bayesian data analysis",
        "Probabilistic programming",
        "Predictive modeling",
        "Evidence-based probability",
        "Bayesian decision-making",
        "Subjective probability models",
        "Bayesian model comparison",
        "Parameter uncertainty quantification",
        "Robust Bayesian analysis",
        "Prior elicitation"
    ]
}


file_path = 'bennett2020.pdf'  # Replace with the path to your PDF file


make_txt_from_pdf(file_path)
txt_files = get_all_txt_files()
print(f'Found {len(txt_files)} text files')


for txt_file in txt_files:
    # get file text
    with open(txt_file, 'r') as file:
        txt = file.read()
    print("Artigo: ",txt_file)
    
    # find FREQUENT terms in text
    print('Frequentist Terms', end=': ')
    freq_terms_in_txt = find_terms_in_text(txt, frequentist_terms)
    for term, freq in freq_terms_in_txt.items():
        print(f'{term}: {freq}')
    
    
    # find BAYESIAN terms in text
    print('Bayesian Terms', end=': ')
    baye_terms_in_txt = find_terms_in_text(txt, bayesian_terms)
    for term, freq in baye_terms_in_txt.items():
        print(f'{term}: {freq}')
        
    # percentage of frequentist terms vs bayesian terms
    freq_terms_count = sum(freq_terms_in_txt.values())
    baye_terms_count = sum(baye_terms_in_txt.values())
    total_terms_count = freq_terms_count + baye_terms_count
    if total_terms_count == 0:
        print('No terms found')
        continue
    freq_terms_percent = (freq_terms_count / total_terms_count) * 100
    baye_terms_percent = (baye_terms_count / total_terms_count) * 100
    print(f'Frequentist terms: {freq_terms_percent:.2f}%')
    print(f'Bayesian terms: {baye_terms_percent:.2f}%')




