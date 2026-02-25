# Topic Modeling Coherence Metrics

## Overview

This document provides a technical and scientific summary of the topic coherence metrics implemented in the `math_investigation/topic_modeling/coherence.py` module. Topic coherence metrics evaluate the semantic quality of topics discovered by Non-negative Matrix Factorization (NMF) and other topic modeling algorithms.

Unlike clustering metrics that focus on partition quality, coherence metrics assess whether the top words in a topic are semantically related and interpretable by humans. These metrics are crucial for:
- Selecting the optimal number of topics
- Comparing different topic modeling algorithms
- Tuning hyperparameters (e.g., regularization)
- Evaluating topic interpretability

## What is Topic Coherence?

**Definition**: Topic coherence measures the degree of semantic similarity between high-scoring words in a topic.

**Intuition**: A coherent topic should contain words that frequently co-occur in documents and are semantically related. For example:
- **High coherence**: {car, vehicle, drive, road, engine}
- **Low coherence**: {car, apple, theory, blue, database}

## Implemented Metrics

### 1. UCI Coherence

#### Mathematical Definition

UCI (University of California, Irvine) coherence is based on Pointwise Mutual Information (PMI) computed over sliding windows:

$$C_{\text{UCI}} = \frac{2}{n(n-1)} \sum_{i=1}^{n-1} \sum_{j=i+1}^{n} \log \frac{P(w_i, w_j) + \epsilon}{P(w_i) \cdot P(w_j)}$$

where:
- $n$ = number of top words in the topic (typically 10-20)
- $w_i, w_j$ = words in the topic
- $P(w_i)$ = probability of word $w_i$ appearing in a sliding window
- $P(w_i, w_j)$ = probability of words $w_i$ and $w_j$ co-occurring in a sliding window
- $\epsilon$ = smoothing factor (typically $10^{-10}$) to avoid log(0)

#### Sliding Window Approach

The probabilities are estimated using a sliding window over documents:

1. **Window size**: Typically 10 tokens (configurable parameter)
2. **Count word occurrences**: Each word presence in a window is counted once
3. **Count co-occurrences**: Each word pair co-occurrence in a window is counted once

$$P(w_i) = \frac{\text{\# windows containing } w_i}{\text{total windows}}$$

$$P(w_i, w_j) = \frac{\text{\# windows containing both } w_i \text{ and } w_j}{\text{total windows}}$$

#### Interpretation

- **Range**: $(-\infty, +\infty)$ in theory, typically $[-15, 15]$ in practice
- **Higher is better**: Positive values indicate words co-occur more than expected by chance
- **Negative values**: Words co-occur less than expected (poor coherence)
- **Zero**: Independent co-occurrence (random association)

#### PMI Intuition

PMI measures the association strength between word pairs:

$$\text{PMI}(w_i, w_j) = \log \frac{P(w_i, w_j)}{P(w_i) \cdot P(w_j)}$$

- **Positive PMI**: Words co-occur more than expected → related
- **Zero PMI**: Words co-occur as expected → independent
- **Negative PMI**: Words co-occur less than expected → unrelated

#### When to Use

- **Best for**: External corpus validation (using original documents)
- **Advantages**:
  - Sensitive to local word associations
  - Reflects human perception of coherence
  - Works with raw text (no preprocessing artifacts)
- **Use cases**:
  - Selecting optimal number of topics
  - Comparing topic models on same corpus
  - Evaluating topic interpretability

#### Computational Complexity

- **Window extraction**: $O(D \cdot L)$ where $D$ = documents, $L$ = average document length
- **Coherence computation**: $O(T \cdot n^2)$ where $T$ = topics, $n$ = top words per topic
- **Total**: $O(D \cdot L + T \cdot n^2)$

---

### 2. UMass Coherence

#### Mathematical Definition

UMass (University of Massachusetts) coherence uses document-level co-occurrence with conditional probabilities:

$$C_{\text{UMass}} = \frac{2}{n(n-1)} \sum_{i=1}^{n-1} \sum_{j=i+1}^{n} \log \frac{D(w_i, w_j) + 1}{D(w_i)}$$

where:
- $D(w_i)$ = number of documents containing word $w_i$
- $D(w_i, w_j)$ = number of documents containing both words $w_i$ and $w_j$
- Smoothing factor +1 prevents log(0)

This can be interpreted as:

$$C_{\text{UMass}} = \frac{2}{n(n-1)} \sum_{i<j} \log P(w_j | w_i)$$

where $P(w_j | w_i)$ is the conditional probability of seeing $w_j$ given $w_i$ appears.

#### Document Co-occurrence Approach

Unlike UCI, UMass uses document-level co-occurrence:

1. **Binary presence**: Check if word appears in document (frequency doesn't matter)
2. **Document frequency**: Count documents containing each word
3. **Co-document frequency**: Count documents containing both words

$$P(w_j | w_i) = \frac{D(w_i, w_j) + 1}{D(w_i)}$$

where $D(w)$ represents document frequency (number of documents containing the word).

#### Interpretation

- **Range**: $(-\infty, 0]$ typically
- **Values closer to 0 are better**: Less negative = higher coherence
- **Negative values**: Indicates conditional probability < 1 (always true unless perfect co-occurrence)
- **Very negative values** (< -10): Poor topic coherence

#### Why Negative Values?

Since $D(w_i, w_j) \leq D(w_i)$, we have:

$$\frac{D(w_i, w_j) + 1}{D(w_i)} \leq \frac{D(w_i) + 1}{D(w_i)} \approx 1$$

Thus $\log(\cdot) \leq 0$ in most cases. The metric measures how much less than 1 this conditional probability is.

#### When to Use

- **Best for**: Quick evaluation using term-document matrix
- **Advantages**:
  - Computationally efficient (no sliding window)
  - Works directly with document-term matrix
  - Stable with small corpora
  - Correlates well with human judgments
- **Use cases**:
  - Fast topic quality assessment
  - Grid search over hyperparameters
  - Large-scale topic modeling

#### Computational Complexity

- **Binary matrix conversion**: $O(D \cdot V)$ where $V$ = vocabulary size
- **Coherence computation**: $O(T \cdot n^2)$
- **Total**: $O(D \cdot V + T \cdot n^2)$
- Generally **faster than UCI** (no window sliding)

---

## Comparison: UCI vs UMass

| Aspect | UCI Coherence | UMass Coherence |
|--------|---------------|-----------------|
| **Co-occurrence level** | Sliding window (local) | Document-level (global) |
| **Value range** | $(-\infty, +\infty)$, often $[-15, 15]$ | $(-\infty, 0]$, often $[-20, 0]$ |
| **Interpretation** | Higher = better | Closer to 0 = better |
| **Requires** | Raw documents + tokenization | Document-term matrix |
| **Computation** | Slower (window sliding) | Faster (matrix operations) |
| **Sensitivity** | Local context, word ordering | Global co-occurrence patterns |
| **Corpus size** | Works with small corpora | Needs reasonable document counts |
| **Human correlation** | High (0.6-0.8) | High (0.6-0.7) |

---

## Theoretical Foundations

### Pointwise Mutual Information (PMI)

PMI is an information-theoretic measure of association:

$$\text{PMI}(x, y) = \log \frac{P(x, y)}{P(x) \cdot P(y)} = \log \frac{P(x|y)}{P(x)} = \log \frac{P(y|x)}{P(y)}$$

**Interpretation**:
- Measures how much more (or less) likely $x$ and $y$ are to co-occur than if they were independent
- Related to mutual information: $I(X;Y) = \sum \sum P(x,y) \cdot \text{PMI}(x,y)$

### Conditional Probability Approach

UMass coherence uses conditional probability:

$$P(w_j | w_i) = \frac{P(w_i, w_j)}{P(w_i)}$$

This measures: "If I see word $w_i$, what's the probability I'll also see $w_j$?"

High conditional probabilities → strong word associations → coherent topics

---

## Usage Guidelines

### Selecting Number of Topics

**Approach**: Compute coherence for different values of $k$ (number of topics)

```python
from math_investigation.topic_modeling.coherence import uci_coherence, umass_coherence

# Range of topics to test
k_values = [3, 5, 7, 10, 15, 20]
coherence_scores = {'k': [], 'uci': [], 'umass': []}

for k in k_values:
    # Train NMF with k topics
    nmf = NMF(n_components=k)
    W = nmf.fit_transform(X)
    H = nmf.components_
    
    # Get top words per topic
    topics = extract_top_words(H, feature_names, n_words=10)
    
    # Compute coherence
    uci_scores = uci_coherence(topics, documents, window_size=10)
    umass_scores = umass_coherence(topics, X, feature_names)
    
    coherence_scores['k'].append(k)
    coherence_scores['uci'].append(np.mean(list(uci_scores.values())))
    coherence_scores['umass'].append(np.mean(list(umass_scores.values())))

# Select k with highest coherence
optimal_k_uci = k_values[np.argmax(coherence_scores['uci'])]
optimal_k_umass = k_values[np.argmax(coherence_scores['umass'])]  # closest to 0
```

**Plot**: Coherence vs. number of topics (look for peak or elbow)

### Evaluating Individual Topics

```python
# Per-topic coherence for interpretation
topics = extract_top_words(H, feature_names, n_words=10)
uci_scores = uci_coherence(topics, documents)

for topic_id, score in uci_scores.items():
    print(f"Topic {topic_id}: {score:.3f}")
    print(f"  Top words: {topics[topic_id]}")
    print()

# Filter out low-coherence topics
good_topics = {tid: words for tid, words in topics.items() 
               if uci_scores[tid] > threshold}
```

### Hyperparameter Tuning

Use coherence metrics for:
- **NMF regularization**: Test different $\alpha$ and $\beta$ values
- **Initialization methods**: Compare random, NNDSVD, etc.
- **Preprocessing**: Compare different stopword lists, min_df/max_df

---

## Implementation Details

### Module: `math_investigation/topic_modeling/coherence.py`

#### Design Principles

- **From-scratch implementation**: No scikit-learn or Gensim dependencies
- **Educational focus**: Clear, readable code with explicit formulas
- **Efficient NumPy operations**: Vectorized computations where possible
- **Type hints and documentation**: Comprehensive docstrings

#### Key Functions

```python
def uci_coherence(
    topics: dict[int, list[str]],
    documents: list[str],
    window_size: int = 10,
) -> dict[int, float]:
    """
    Args:
        topics: {topic_idx: [top_words]}
        documents: Original document texts
        window_size: Sliding window size (default: 10)
    
    Returns:
        {topic_idx: coherence_score}
    """

def umass_coherence(
    topics: dict[int, list[str]],
    doc_term_matrix: np.ndarray,
    feature_names: list[str],
) -> dict[int, float]:
    """
    Args:
        topics: {topic_idx: [top_words]}
        doc_term_matrix: Document-term matrix (will be binarized)
        feature_names: Vocabulary in order
    
    Returns:
        {topic_idx: coherence_score}
    """
```

#### Preprocessing Steps

Both metrics include:
- **Tokenization**: Lowercase, remove punctuation, extract words
- **Stopword removal**: Filter common words using `STOPWORDS` set
- **Minimum word length**: 2+ characters (configurable)

#### Optimization Considerations

For large corpora:
- **UCI**: Consider sampling documents or limiting window count
- **UMass**: Sparse matrix operations for efficiency
- **Caching**: Store co-occurrence counts if computing multiple coherence values

---

## Validation and Benchmarks

### Human Correlation Studies

Research shows coherence metrics correlate with human topic interpretability:

| Metric | Correlation with Human Judgments |
|--------|----------------------------------|
| UCI Coherence | $r = 0.65 - 0.80$ |
| UMass Coherence | $r = 0.60 - 0.75$ |
| C_V (not implemented) | $r = 0.70 - 0.85$ |

*Source: Röder et al. (2015)*

### Expected Value Ranges

Typical coherence values for real-world topics:

| Quality | UCI Coherence | UMass Coherence |
|---------|---------------|-----------------|
| Excellent | > 5 | > -2 |
| Good | 2 to 5 | -2 to -5 |
| Moderate | 0 to 2 | -5 to -10 |
| Poor | < 0 | < -10 |

*Note: These are approximate guidelines; actual ranges depend on corpus characteristics*

---

## Limitations and Considerations

### UCI Coherence

**Limitations**:
- Sensitive to window size parameter
- Computationally expensive for large corpora
- Requires well-preprocessed text
- May be affected by document length distribution

**Best practices**:
- Use window_size=10 as default (validated in literature)
- Ensure consistent tokenization
- Remove very frequent and very rare words
- Consider downsampling for very large corpora

### UMass Coherence

**Limitations**:
- Less sensitive to local context
- Assumes binary word presence (ignores frequency)
- Can be unstable with very small corpora
- Biased toward frequent words

**Best practices**:
- Ensure adequate corpus size (100+ documents minimum)
- Use appropriate min_df/max_df thresholds
- Validate results with multiple metrics
- Consider document length normalization

---

## Advanced Topics

### C_V Coherence (Not Implemented)

C_V coherence combines multiple measures and typically achieves highest human correlation:

$$C_V = \text{cosine}(\vec{s}_{\text{NPMI}}, \vec{s}_{\text{context}})$$

where NPMI is normalized PMI and context vectors capture semantic relationships.

**Why not implemented**: Requires external semantic models (word embeddings) and is more complex. UCI and UMass are sufficient for most TFG applications.

### Topic Diversity Metrics

In addition to coherence, topic diversity measures uniqueness:

$$\text{Diversity} = \frac{1}{T} \sum_{t=1}^{T} \frac{|\text{unique words in topic } t|}{n}$$

High diversity + high coherence = optimal topic model

---

## Integration with Math Investigation

### Question Classification Pipeline

1. **NMF Topic Modeling**: Decompose question embeddings
2. **Coherence Evaluation**: Select optimal number of topics
3. **Topic Assignment**: Map questions to dominant topic
4. **Difficulty Clustering**: Within-topic K-Means/FCM clustering

Example workflow:
```python
# scripts/train_difficulty_centroids.py integration
from math_investigation.topic_modeling.coherence import uci_coherence
from math_investigation.clustering.kmeans import KMeans

# 1. Topic modeling
topics = extract_top_words(H, feature_names, n_words=10)
coherence = uci_coherence(topics, questions)

# 2. Filter high-coherence topics
good_topics = [t for t in range(n_topics) if coherence[t] > threshold]

# 3. Cluster within topics
for topic_id in good_topics:
    topic_questions = W[:, topic_id] > threshold
    kmeans = KMeans(n_clusters=3)  # Easy/Medium/Hard
    labels = kmeans.fit_predict(X[topic_questions])
```

### Chatbot Enhancement

Topic coherence helps the chatbot:
- **Question routing**: High-coherence topics → reliable classification
- **Content organization**: Group similar questions by topic
- **Quality assessment**: Monitor topic coherence over time as new questions arrive

---

## References

### Academic Sources

1. **UCI Coherence**: Newman, D., Lau, J.H., Grieser, K., & Baldwin, T. (2010). "Automatic evaluation of topic coherence". *Human Language Technologies: The 2010 Annual Conference of the North American Chapter of the ACL*, 100-108.

2. **UMass Coherence**: Mimno, D., Wallach, H., Talley, E., Leenders, M., & McCallum, A. (2011). "Optimizing semantic coherence in topic models". *Proceedings of EMNLP 2011*, 262-272.

3. **Coherence Survey**: Röder, M., Both, A., & Hinneburg, A. (2015). "Exploring the space of topic coherence measures". *Proceedings of WSDM 2015*, 399-408.

4. **PMI Theory**: Church, K.W., & Hanks, P. (1990). "Word association norms, mutual information, and lexicography". *Computational Linguistics*, 16(1), 22-29.

### Related Documentation

- [NMF Algorithm Implementation](./nmf_algorithm.md) *(to be created)*
- [Clustering Validation Metrics](./clustering_metrics.md) *(created)*
- [Topic Modeling Experiments](./topic_modeling_experiments.md) *(to be created)*
- [Question Classification Pipeline](./question_classification.md) *(to be created)*

---

## Appendix: Formula Summary

### UCI Coherence

$$C_{\text{UCI}}(T) = \frac{2}{n(n-1)} \sum_{i=1}^{n-1} \sum_{j=i+1}^{n} \text{PMI}(w_i, w_j)$$

$$\text{PMI}(w_i, w_j) = \log \frac{P(w_i, w_j) + \epsilon}{P(w_i) \cdot P(w_j)}$$

$$P(w) = \frac{\text{\# windows containing } w}{\text{total windows}}$$

### UMass Coherence

$$C_{\text{UMass}}(T) = \frac{2}{n(n-1)} \sum_{i=1}^{n-1} \sum_{j=i+1}^{n} \log \frac{D(w_i, w_j) + 1}{D(w_i)}$$

$$D(w) = \text{\# documents containing } w$$

$$D(w_i, w_j) = \text{\# documents containing both } w_i \text{ and } w_j$$

---

*Last updated: February 5, 2026*
