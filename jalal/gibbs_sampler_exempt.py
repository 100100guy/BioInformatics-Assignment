import random

def read_sequences(filepath):
    with open(filepath, 'r') as file:
        sequences = [line.strip() for line in file.readlines()]
    return sequences

def randomly_select_kmers(sequences, k):
    return [seq[start:start+k] for seq in sequences for start in [random.randint(0, len(seq) - k)]]

def create_profile(motifs, k, i):
    profile_matrix = [[1 for _ in range(k)] for _ in range(4)]
    nucleotides = 'ACGT'
    for index, motif in enumerate(motifs):
        if index != i:
            for position, nucleotide in enumerate(motif):
                row = nucleotides.index(nucleotide)
                profile_matrix[row][position] += 1

    for position in range(k):
        total = sum(profile_matrix[row][position] for row in range(4))
        for row in range(4):
            profile_matrix[row][position] /= total
    return profile_matrix

def score(motifs, k):
    consensus = ''
    score = 0
    for i in range(k):
        col = [motif[i] for motif in motifs]
        max_freq = max(col, key=col.count)
        consensus += max_freq
        score += sum(1 for base in col if base != max_freq)
    return score, consensus

def calculate_kmer_probabilities(sequence, k, profile_matrix):
    probabilities = []
    for i in range(len(sequence) - k + 1):
        prob = 1.0
        for j in range(k):
            nucleotide = sequence[i+j]
            if nucleotide == 'A':
                prob *= profile_matrix[0][j]
            elif nucleotide == 'C':
                prob *= profile_matrix[1][j]
            elif nucleotide == 'G':
                prob *= profile_matrix[2][j]
            elif nucleotide == 'T':
                prob *= profile_matrix[3][j]
        probabilities.append(prob)
    total = sum(probabilities)
    probabilities = [p/total for p in probabilities]
    return probabilities

def profile_weighted_random_kmer(sequence, k, profile_matrix):
    probabilities = calculate_kmer_probabilities(sequence, k, profile_matrix)
    return random.choices([sequence[i:i+k] for i in range(len(sequence) - k + 1)], weights=probabilities, k=1)[0]

def gibbs_sampler(sequences, k, t, N, num_exempt):
    motifs = randomly_select_kmers(sequences, k)
    best_motifs = motifs[:]
    best_score, _ = score(best_motifs, k)
    for j in range(N):
        exempt_indices = random.sample(range(t), num_exempt)
        for i in range(t):
            if i not in exempt_indices:
                temp_motifs = [motif for index, motif in enumerate(motifs) if index not in exempt_indices] + [motifs[x] for x in exempt_indices]
                profile_matrix = create_profile(temp_motifs, k, None)
                motifs[i] = profile_weighted_random_kmer(sequences[i], k, profile_matrix)
        current_score, _ = score(motifs, k)
        if current_score < best_score:
            best_motifs = motifs[:]
            best_score = current_score
    return best_motifs, best_score

def run_gibbs_sampler_with_scores(filepath, k, N, num_exempt):
    sequences = read_sequences(filepath)
    t = len(sequences)
    best_motifs, best_score = gibbs_sampler(sequences, k, t, N, num_exempt)
    _, consensus = score(best_motifs, k)
    return best_motifs, best_score, consensus

k = 8
N = 10000
num_exempt = 8
best_motifs, best_score, consensus = run_gibbs_sampler_with_scores('hm03.txt', k, N, num_exempt)
print(f"Best motifs: {best_motifs}")
print(f"Score: {best_score}")
print(f"Consensus: {consensus}")