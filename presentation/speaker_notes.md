# Speaker Notes: Privacy-Preserving Sealed-Bid Auctions

Final presentation, CS670. About **18 minutes**, which leaves room inside a 15–20 minute slot. Slide numbers are PDF page numbers in `presentation/slides.pdf`.

The slides do not say who presents what. The split below is only a suggestion for the recording; change it freely. Each part starts on a section slide, which gives clean cut points.

| Part | Slides | Suggested speaker | Time |
|---|---|---|---|
| 1. The problem and our setting | 1–5 | Aarav Oswal | 3:15 |
| 2. Computing on secret shares | 6–10 | Poorvie Sadagopan | 4:00 |
| 3. The auction algorithm | 11–18 | Ch. Rishitha | 5:30 |
| 4. Evaluation and conclusions | 19–28 | R. Charan | 5:15 |
| | | **Total** | **18:00** |

Times are targets. The points under each slide are a guide to say in your own words, not a script to read.

---

## Part 1: The problem and our setting (3:15)

### Slide 1: Title (0:20)
- "Our project is a privacy-preserving sealed-bid auction: an auction where nobody, not even the servers running it, ever sees an individual bid."
- Introduce the four members in one line.

### Slide 2: Section slide (0:00)

### Slide 3: The auctioneer's dilemma (1:00)
- In a sealed-bid auction someone has to open every envelope to decide who won. That person learns every bidder's valuation and strategy.
- In a **Vickrey** auction the winner pays the *second*-highest bid. A dishonest auctioneer can quietly raise that price and nobody can tell.
- Even an honest auctioneer is a single point of failure.
- Key idea: **an auction is just a secure maximum.** If we can find the maximum of hidden numbers, we have a private auction.

### Slide 4: Goal and threat model (0:55)
- Goal: reveal **the winner and the price, and nothing else**. No ranking of losers, not even who tied.
- Three servers do the computation. At most one is corrupted, and it is **semi-honest**: it follows the protocol but tries to learn from what it sees. Two servers working together are outside our model.
- What we built: the Kurosawa–Ogata bit-slice auction on the MP-SPDZ framework, for first-price and Vickrey, in two versions, plus a baseline to compare against.

### Slide 5: System architecture (1:00)
- Left to right: each bidder splits its bid into three random-looking shares and sends one to each server. Then the bidder is done.
- The three servers compute the auction together on the shares.
- Only two values ever come out: the winner and the price.
- **Hand-off:** "Next we'll see how three servers can compute on numbers that none of them can see."

---

## Part 2: Computing on secret shares (4:00)

### Slide 6: Section slide (0:00)

### Slide 7: Replicated secret sharing (1:00)
- A secret *x* is split into three shares that add up to *x*. Each server holds **two** of the three.
- One server is always missing one share, so what it holds looks completely random. It learns nothing.
- Two servers together could rebuild *x*. That's why we need at most one bad server.
- The same idea works with XOR instead of addition, for single bits. That gives us the "binary" version later.

### Slide 8: Adding and multiplying (1:15)
- **Adding** is free: each server adds the shares it holds, and the results are shares of the sum. No messages.
- **Multiplying** is the interesting part. Multiplying out (x₀+x₁+x₂)(y₀+y₁+y₂) gives 9 cross terms, shown in the grid. Each colour is one server: each server holds enough to compute 3 of them, and together they cover all 9.
- Each server then adds a fresh random mask (three random numbers that sum to zero) and sends one number to its neighbour. Afterwards everyone again holds two shares of the product.
- So every multiplication costs **one round of communication**. Many independent multiplications can share the same round.
- On bits, AND is multiplication, NOT is 1 − x, and OR can be written with ANDs. So any algorithm built from AND, OR and NOT can run on hidden data.
- The cost of an algorithm is the number of ANDs (amount of data) and the number of rounds (waiting time on a network).

### Slide 9: Workflow of one auction (0:45)
- Six steps. On the bidder's device: (1) write the bid in binary, (2) split each bit into three shares and send one to each server.
- On the servers: (3) combine the shares so each holds two of three, (4) scan the bits to find the highest bid, (5) break ties and, for Vickrey, scan again for the price, (6) open only the winner and the price.
- The steps are the same for every input. The servers do not know the bids, so they always do exactly the same work, and the running time reveals nothing.

### Slide 10: Bidder side (1:00)
- The bidder shares the **bits** of its bid, not the number itself. Writing 13 as 1101 is trivial for the bidder, who knows the bid. The servers then receive shares of the bits directly.
- The example on the right: a bit equal to 1 becomes three large numbers. Each server sees only one of them, and it looks the same whether the bit is 0 or 1. Only the sum of all three reveals the bit.
- In the binary version the same thing happens with XOR shares.
- **Hand-off:** "Now that the servers hold shares of every bit, here is how they find the winner."

---

## Part 3: The auction algorithm (5:30)

### Slide 11: Section slide (0:00)

### Slide 12: From comparisons to a single scan (0:50)
- The naive approach compares bids two at a time, like a tournament.
- Kurosawa and Ogata's idea: look at all bids together, one bit position at a time, from the highest bit down. Keep a list of bidders who can still win. At each bit, if any of them has a 1, everyone still in with a 0 is out.
- Only AND and OR are needed.
- **The catch:** "*if* someone has a 1" is a branch on a secret value. The servers can't branch, because they can't see the value. We need a version where the same operations run whatever the bids are.

### Slide 13: Worked example, A = 11, B = 13, C = 9 (1:00)
- Walk the columns from the highest bit. Blue cells are bidders still in.
- Bit 3: everyone has a 1, so nobody is dropped.
- Bit 2: only B has a 1, so A and C are out.
- Bit 1: B has a 0, but B is the only one left, so nobody has a 1 and **nobody is dropped**.
- Bit 0: B stays. The bottom row reads 1101 = 13, the maximum.
- Key case is bit 1: when nobody still in has a 1, the mask is **kept**, not emptied.

### Slide 14: One step, without branching (1:00)
- *t* = S AND bit: who is still in *and* has a 1 here.
- The OR box asks "does anyone in *t* have a 1?" That answer is c_j.
- New S = S − c_j·(S − t). If c_j is 1, this gives *t*. If c_j is 0, it gives S unchanged. It's the same arithmetic either way, so there's no branch.
- Writing it this way needs only one multiplication per bidder for the update.

### Slide 15: The OR tree (0:40)
- To OR together *n* secret bits, combine them in pairs, then pairs of pairs. Each OR is one AND.
- That's *n* − 1 ANDs, but only log₂ *n* rounds, because each level runs in parallel.
- Bonus: c_j is exactly bit *j* of the highest bid, so we get the maximum for free.

### Slide 16: Ties (0:45)
- If bidders tie, several are still in at the end. Opening that list would reveal who tied.
- Instead we keep only the first one still in: bidder *i* wins if it is in and nobody before it is.
- In the example, bidders 1, 3 and 4 tied, but only "1" is opened.

### Slide 17: Vickrey, a second scan (0:45)
- To find the second-highest bid, wipe the winner's bits to zero. This uses AND with NOT-winner, so nobody learns whose bits were wiped.
- Run the scan again. The new maximum is the price.
- The first maximum (the winning bid) is never opened.
- Edge cases work automatically: a tie at the top gives price = top bid; a single bidder pays 0.

### Slide 18: The output (0:30)
- At the end, the servers combine their shares of just two values: the winner's index and the price.
- We confirmed with the framework's own count that nothing else is opened.
- Who sees what: a bidder sees its own bid and the result; one server sees only random shares and the result.
- What the result itself implies, for example that every losing bid is at most the price, isn't a leak. Every auction reveals that.
- **Hand-off:** "Now, how well does it perform?"

---

## Part 4: Evaluation and conclusions (5:15)

### Slide 19: Section slide (0:00)

### Slide 20: Baseline (0:30)
- To judge the bit-slice method fairly, we built a standard alternative: a knockout tournament using the framework's built-in secure comparison.
- Same inputs, same tie rule, same outputs, built in both versions.

### Slide 21: Same circuit, two domains (0:45)
- In the normal (arithmetic) version, every secret is a 64-bit number. Our algorithm only ever ANDs single bits, so 63 of every 64 bits sent are wasted.
- In the binary version each secret is one bit, and bit *j* of all bidders is packed into one word. Each AND then costs 1 bit instead of 64.
- Same algorithm, same number of ANDs, 61 times less data.

### Slide 22: Scaling with the number of bidders (0:40)
- Top: rounds. Bit-slice (blue) grows much faster than the tournament (orange).
- Bottom: data, log scale. The binary versions (dashed) are almost 100 times below the arithmetic ones.
- The number of ANDs we measured matches our formula exactly.

### Slide 23: Results at 128 bidders, 32-bit bids (0:50)
- The binary version sends 61× less data. But the tournament gains just as much from the binary version, so on data the two methods are close.
- **Rounds decide the time.** Bit-slice has to handle the bits one after another, so its rounds grow with the bid length. The tournament needs far fewer.
- On a slow network (50 ms delay), bit-slice takes about 29 seconds and the tournament 4–6.

### Slide 24: Network time and malicious security (0:40)
- Left: estimated time on a fast and a slow network, from the measured rounds and data. The tournament wins on both.
- Right: we also ran the same programs with protection against a cheating server. That costs about 6× more data in the arithmetic version, and stays small in the binary version.

### Slide 25: How we checked correctness (0:30)
- Everything is compared with the plain auction rule.
- We checked the formulas on plain bits for every small input; we ran the real three-server protocol on edge cases like ties, a single bidder and all-zero bids; we confirmed only two values are opened; and every benchmark result was checked too.

### Slide 26: What we learned (0:40)
- **The domain matters more than the algorithm**: 61× from the domain, about 10% between the two methods.
- **Bit-slice loses on time**, because its scan is sequential in the bid length. The original "7× faster" claim from 2002 was against comparison methods of that time.
- Bit-slice still has strengths: fewest ANDs at large scale in the binary version, only two values opened, and it needs nothing but multiplication.
- And a general lesson: on secret data, every "if" has to become arithmetic, so the same operations run whatever the bids are.

### Slide 27: Limitations and future work (0:35)
- Limitations: bidders are trusted to send valid bits; a cheating server could swap its own input share; all servers ran on one machine.
- Future work: authenticated bidder inputs, public verifiability, a faster scan that handles several bits at once, and more servers.
- Summary line: "Three servers run a first-price or Vickrey auction without any of them seeing a bid, and open only the winner and the price."

### Slide 28: Thank you (0:05)
- "Thank you. The code is on GitHub at the link shown. We're happy to take questions."

---

## Likely questions and short answers

**Why three servers and not two?**
With three servers and an honest majority, multiplication is very cheap: one message per server. Two-party protocols need heavier tools like oblivious transfer or garbled circuits.

**What stops a server from cheating?**
In our main model it is assumed semi-honest. We also ran everything with protocols that detect a cheating server and abort. One gap remains: a server could replace its own input share of a bid.

**Does the running time leak the bids?**
No. The servers always run the same operations for a given number of bidders and bid length, so rounds, messages and sizes are the same for every set of bids.

**Why is the tournament faster if bit-slice was proposed as faster?**
The bit-slice scan has to process the bits one after another, so its rounds grow with the bid length. Modern secure comparison needs only about log k rounds. The original comparison was against 2002-era methods.

**What does the price reveal about losing bids?**
Only what any auction reveals: in first-price, every losing bid is at most the price; in Vickrey, the price is the second-highest bid.

**What happens with a bid of 0, or all bids equal?**
Both work: all-equal bids are a tie, so the lowest index wins and pays that bid. Zero bids are just bits that are all 0. We tested these cases on the real protocol.

---

## Recording checklist

- [ ] Open `presentation/slides.pdf` in full-screen mode. Each part starts on its section slide (pages 2, 6, 11, 19).
- [ ] Keep each part within ±20 s of its target, for about 18 minutes in total.
