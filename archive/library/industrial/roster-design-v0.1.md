# Industrial Library Roster Design v0.1

Status: `operator-review`
Era: `industrial`
Range: 1815 AD to 1991 AD
Architecture contract: `archive/library/industrial/architecture-contract-v0.1.md`
Gate: `operator-review-before-metadata-mutation`

## Authority Boundary

This packet freezes the first full Industrial roster design for operator
review. It does not
mutate `archive/library/library-registry.json`, generate indexes, download
sources, admit source bodies, ingest into the private Archive, stage, commit,
push, or publish.

The design is intentionally above the contract minimum: 96 authorities, with
literature, testimony, and interiority structurally central. Every candidate is
classified no higher than `roster-ready-proposal`; rights and edition notes are
triage signals, not body-research evidence.

## Design Thesis

Industrial, 1815-1991, should preserve the original-era textual witnesses by
which industrial modernity described itself and became governable: novels,
poems, speeches, manifestos, scientific treatises, political programs, labor
documents, colonial and anti-colonial witness, war testimony, rights texts,
environmental warnings, and institutional language.

Literature is central because the Industrial era's most durable civilizational
memory often appears as interior life under mass society: factory discipline,
urban crowding, imperial encounter, racial order, gender constraint, war,
revolution, bureaucracy, and technological danger.

## Lane Floors And Counts

| Lane | Count | Design role |
| --- | ---: | --- |
| `civilization-memory-literature` | 43 | Novels, poetry, drama, literary testimony, modernist and postcolonial interiority |
| `industrial-political-economy` | 6 | Capitalism, socialism, labor value, bureaucracy, democratic society |
| `mass-politics-ideology` | 7 | Revolution, nationalism, fascism, communism, anti-colonial state formation |
| `state-law-constitution` | 3 | Codes, rights, constitutional democracy, legal reform |
| `science-technology-system` | 5 | Evolution, electricity, computation, nuclear modernity, statistics |
| `labor-social-question` | 3 | Industrial city, unions, social investigation, welfare |
| `empire-colonial-administration` | 0 | Imperial rule, race, slavery aftermath, colonial administration; represented as a secondary function through literary, war, and decolonization rows |
| `indigenous-colonized-witness` | 8 | Native, Black Atlantic, Asian, African, and Caribbean witness |
| `war-revolution-violence` | 4 | Total war, genocide, survivor and strategic testimony |
| `religion-moral-order` | 2 | Secularization, conscience, religious-political modernity |
| `media-propaganda-public` | 0 | Information order and language politics; represented as a secondary function through literary and political rows |
| `international-order-decolonization` | 9 | UN, nonalignment, decolonization, Cold War order |
| `gender-family-education` | 4 | Feminism, family, education, social reproduction |
| `environment-extraction-infrastructure` | 2 | Ecology, extraction, industrial toxicity |

Several authorities carry secondary functions; the counts above use each
candidate's primary roster function.

## 96-Authority Roster

| # | Authority | Primary function | Region/system | First-source target | Rights/edition triage |
| ---: | --- | --- | --- | --- | --- |
| 1 | Jane Austen | `civilization-memory-literature` | Britain | `Persuasion` | public-domain likely |
| 2 | Mary Shelley | `civilization-memory-literature` | Britain | `Frankenstein` | public-domain likely |
| 3 | Alexander Pushkin | `civilization-memory-literature` | Russia | `Eugene Onegin`; selected poems | original/translation separation |
| 4 | Honore de Balzac | `civilization-memory-literature` | France | `Pere Goriot`; selected `Comedie humaine` | public-domain likely; translation review |
| 5 | Victor Hugo | `civilization-memory-literature` | France | `Les Miserables` | public-domain likely; translation review |
| 6 | Charles Dickens | `civilization-memory-literature` | Britain | `Hard Times`; `Bleak House` | public-domain likely |
| 7 | Charlotte Bronte | `civilization-memory-literature` | Britain | `Jane Eyre` | public-domain likely |
| 8 | Emily Bronte | `civilization-memory-literature` | Britain | `Wuthering Heights` | public-domain likely |
| 9 | George Eliot | `civilization-memory-literature` | Britain | `Middlemarch` | public-domain likely |
| 10 | Gustave Flaubert | `civilization-memory-literature` | France | `Madame Bovary` | public-domain likely; translation review |
| 11 | Fyodor Dostoevsky | `civilization-memory-literature` | Russia | `Notes from Underground`; `Brothers Karamazov` | translation rights require review |
| 12 | Leo Tolstoy | `civilization-memory-literature` | Russia | `War and Peace`; `Anna Karenina` | translation rights require review |
| 13 | Henrik Ibsen | `civilization-memory-literature` | Scandinavia | `A Doll's House`; `An Enemy of the People` | public-domain likely; translation review |
| 14 | Anton Chekhov | `civilization-memory-literature` | Russia | selected plays and stories | translation rights require review |
| 15 | Rabindranath Tagore | `civilization-memory-literature` | South Asia | `Gitanjali`; `Nationalism` | mixed public-domain; edition review |
| 16 | Lu Xun | `civilization-memory-literature` | China | `A Madman's Diary`; selected stories | rights/translation risk |
| 17 | Natsume Soseki | `civilization-memory-literature` | Japan | `Kokoro` | translation rights risk |
| 18 | Premchand | `civilization-memory-literature` | South Asia | `Godan`; selected stories | Hindi/Urdu and translation review |
| 19 | Machado de Assis | `civilization-memory-literature` | Brazil | `Dom Casmurro`; `Posthumous Memoirs` | public-domain likely; translation review |
| 20 | Jose Rizal | `civilization-memory-literature` | Philippines | `Noli Me Tangere`; `El Filibusterismo` | public-domain likely; translation review |
| 21 | Walt Whitman | `civilization-memory-literature` | United States | `Leaves of Grass` | public-domain likely |
| 22 | Emily Dickinson | `civilization-memory-literature` | United States | poems | edition history requires review |
| 23 | Herman Melville | `civilization-memory-literature` | United States/sea power | `Moby-Dick` | public-domain likely |
| 24 | Mark Twain | `civilization-memory-literature` | United States | `Huckleberry Finn`; `Life on the Mississippi` | public-domain likely |
| 25 | W. E. B. Du Bois | `indigenous-colonized-witness` | Black Atlantic/United States | `The Souls of Black Folk` | public-domain likely |
| 26 | Frederick Douglass | `indigenous-colonized-witness` | United States/Black Atlantic | `Narrative`; speeches | public-domain likely |
| 27 | Harriet Jacobs | `gender-family-education` | United States/Black Atlantic | `Incidents in the Life of a Slave Girl` | public-domain likely |
| 28 | Sojourner Truth textual tradition | `indigenous-colonized-witness` | United States/Black Atlantic | speeches | speech textual tradition needs edition review |
| 29 | Karl Marx | `industrial-political-economy` | Transnational socialism | `Capital`; `Communist Manifesto` | public-domain originals; translation review |
| 30 | Friedrich Engels | `industrial-political-economy` | Britain/Germany | `Condition of the Working Class in England` | public-domain likely |
| 31 | John Stuart Mill | `state-law-constitution` | Britain/liberalism | `On Liberty`; `Subjection of Women` | public-domain likely |
| 32 | Alexis de Tocqueville | `industrial-political-economy` | France/United States | `Democracy in America`; `Old Regime` | translation rights review |
| 33 | Max Weber | `industrial-political-economy` | Germany | `Protestant Ethic`; political essays | translation rights review |
| 34 | Emile Durkheim | `industrial-political-economy` | France | `Division of Labor`; `Suicide` | translation rights review |
| 35 | Sigmund Freud | `religion-moral-order` | Central Europe | `Civilization and Its Discontents` | rights and translation risk |
| 36 | Friedrich Nietzsche | `religion-moral-order` | Germany | `Genealogy of Morals`; `Zarathustra` | translation rights review |
| 37 | Stalin / Soviet party-state textual tradition | `mass-politics-ideology` | Russia/Soviet world | selected speeches, party reports, constitutional and planning texts | rights/edition and harm-context review |
| 38 | Charles Darwin | `science-technology-system` | Britain/science | `Origin of Species`; `Descent of Man` | public-domain likely |
| 39 | Alfred Russel Wallace | `science-technology-system` | Britain/maritime Asia | `Malay Archipelago` | public-domain likely |
| 40 | Michael Faraday | `science-technology-system` | Britain/public science | lectures and experimental writings | public-domain likely |
| 41 | Charles Babbage | `science-technology-system` | Britain/computation | `Economy of Machinery and Manufactures` | public-domain likely |
| 42 | Florence Nightingale | `labor-social-question` | Britain/statistics | `Notes on Nursing`; sanitary reports | public-domain likely |
| 43 | Henry David Thoreau | `environment-extraction-infrastructure` | United States | `Civil Disobedience`; `Walden` | public-domain likely |
| 44 | John Ruskin | `industrial-political-economy` | Britain | `Unto This Last` | public-domain likely |
| 45 | William Morris | `labor-social-question` | Britain/socialist aesthetics | `News from Nowhere`; essays | public-domain likely |
| 46 | Mohandas K. Gandhi | `international-order-decolonization` | South Asia | `Hind Swaraj`; speeches | mixed rights; source-specific review |
| 47 | Jawaharlal Nehru | `international-order-decolonization` | South Asia | `Discovery of India`; speeches | rights risk |
| 48 | B. R. Ambedkar | `state-law-constitution` | South Asia | `Annihilation of Caste`; constitutional speeches | rights/source review |
| 49 | Sun Yat-sen | `mass-politics-ideology` | China | `Three Principles of the People` | edition/translation review |
| 50 | Mao Zedong | `mass-politics-ideology` | China | selected writings | high rights/edition risk |
| 51 | Fukuzawa Yukichi | `international-order-decolonization` | Japan | `Encouragement of Learning`; civilization essays | translation rights review |
| 52 | Mustafa Kemal Ataturk | `mass-politics-ideology` | Turkey | `Nutuk`; speeches | translation/government rights review |
| 53 | Vladimir Lenin | `mass-politics-ideology` | Russia/Soviet | `Imperialism`; `State and Revolution` | public-domain varies; translation review |
| 54 | Rosa Luxemburg | `mass-politics-ideology` | Europe/socialism | `Reform or Revolution`; `Junius Pamphlet` | public-domain likely; translation review |
| 55 | Hannah Arendt | `war-revolution-violence` | Europe/United States | `Origins of Totalitarianism` | rights restricted |
| 56 | Adolf Hitler / Nazi textual tradition | `war-revolution-violence` | Germany/fascism | `Mein Kampf`; party documents | harm/context and rights controls |
| 57 | Winston Churchill | `war-revolution-violence` | Britain/empire/war | wartime speeches | speech/edition rights review |
| 58 | Primo Levi | `war-revolution-violence` | Italy/genocide testimony | `Survival in Auschwitz` | rights restricted |
| 59 | Frantz Fanon | `indigenous-colonized-witness` | Caribbean/North Africa | `Wretched of the Earth`; `Black Skin, White Masks` | rights restricted |
| 60 | Nelson Mandela | `international-order-decolonization` | South Africa | trial statement; speeches | rights/source review |
| 61 | Emile Zola | `civilization-memory-literature` | France | `Germinal`; `J'accuse` | public-domain likely |
| 62 | Thomas Hardy | `civilization-memory-literature` | Britain | `Tess`; `Jude the Obscure` | public-domain likely |
| 63 | Oscar Wilde | `civilization-memory-literature` | Ireland/Britain | plays; `De Profundis` | public-domain likely |
| 64 | Joseph Conrad | `civilization-memory-literature` | Britain/empire | `Heart of Darkness`; `Lord Jim` | public-domain likely |
| 65 | Virginia Woolf | `civilization-memory-literature` | Britain | `A Room of One's Own`; early novels | jurisdiction and edition review |
| 66 | James Joyce | `civilization-memory-literature` | Ireland | `Dubliners`; `Ulysses` | rights vary by jurisdiction |
| 67 | Franz Kafka | `civilization-memory-literature` | Central Europe | `The Trial`; stories | translation rights risk |
| 68 | William Faulkner | `civilization-memory-literature` | United States | `The Sound and the Fury`; stories | rights restricted |
| 69 | George Orwell | `civilization-memory-literature` | Britain/empire/media language | `Politics and the English Language`; `Animal Farm`; `1984` | rights vary by jurisdiction |
| 70 | Simone de Beauvoir | `gender-family-education` | France | `The Second Sex` | rights restricted |
| 71 | Aime Cesaire | `indigenous-colonized-witness` | Caribbean/France | `Discourse on Colonialism` | rights restricted |
| 72 | Leopold Sedar Senghor | `indigenous-colonized-witness` | West Africa/France | poems; political essays | rights restricted |
| 73 | C. L. R. James | `indigenous-colonized-witness` | Caribbean/Black Atlantic | `The Black Jacobins` | rights restricted |
| 74 | Chinua Achebe | `civilization-memory-literature` | West Africa | `Things Fall Apart` | rights restricted |
| 75 | Ngugi wa Thiong'o | `civilization-memory-literature` | East Africa | `A Grain of Wheat`; language essays | rights restricted |
| 76 | Jose Marti | `international-order-decolonization` | Cuba/Latin America | `Nuestra America`; selected essays | public-domain likely; translation review |
| 77 | Gabriel Garcia Marquez | `civilization-memory-literature` | Colombia/Latin America | `One Hundred Years of Solitude` | rights restricted |
| 78 | Rachel Carson | `environment-extraction-infrastructure` | United States/ecology | `Silent Spring` | rights restricted |
| 79 | Albert Einstein | `science-technology-system` | Transnational science | relativity essays; nuclear-era letters | mixed rights |
| 80 | Universal Declaration of Human Rights drafting tradition | `international-order-decolonization` | International order | UDHR and drafting documents | institutional text; source review |
| 81 | Olive Schreiner | `civilization-memory-literature` | South Africa | `The Story of an African Farm`; selected political writings | public-domain likely; edition review |
| 82 | Elizabeth Cady Stanton | `gender-family-education` | United States | Seneca Falls materials; speeches | public-domain likely |
| 83 | Ida B. Wells | `indigenous-colonized-witness` | United States/Black Atlantic | anti-lynching pamphlets | public-domain likely |
| 84 | Zitkala-Sa | `civilization-memory-literature` | Indigenous North America | `American Indian Stories`; essays | public-domain likely; edition review |
| 85 | Marcus Garvey | `mass-politics-ideology` | Black Atlantic | speeches and UNIA writings | rights/source review |
| 86 | Ho Chi Minh | `international-order-decolonization` | Vietnam | declarations; prison poems; selected writings | rights/translation review |
| 87 | Kwame Nkrumah | `international-order-decolonization` | West Africa | independence speeches; `Neo-Colonialism` | rights restricted |
| 88 | Sembene Ousmane | `civilization-memory-literature` | West Africa | `God's Bits of Wood`; selected stories | rights/translation risk |
| 89 | Naguib Mahfouz | `civilization-memory-literature` | Egypt/Arabic literature | `Cairo Trilogy`; selected novels | rights/translation risk |
| 90 | Sadegh Hedayat | `civilization-memory-literature` | Iran/Persian modernity | `The Blind Owl`; selected stories | rights/translation risk |
| 91 | Qiu Jin | `gender-family-education` | China | poems, essays, revolutionary writings | edition/translation review |
| 92 | Kang Youwei and Liang Qichao reform textual tradition | `state-law-constitution` | China | reform memorials and essays | composite tradition; translation review |
| 93 | Booker T. Washington | `labor-social-question` | United States/Black education | `Up from Slavery`; Atlanta Exposition address | public-domain likely |
| 94 | Anna Akhmatova | `civilization-memory-literature` | Russia/Soviet world | `Requiem`; selected poems | rights/translation review |
| 95 | Jorge Luis Borges | `civilization-memory-literature` | Argentina/Latin America | `Ficciones`; selected essays | rights/translation risk |
| 96 | United Nations Charter / San Francisco conference tradition | `international-order-decolonization` | International order | UN Charter; conference records | institutional text; source review |

## Reserve Alternates

Reserve candidates repair balance or rights blockers. They should not enter
merely for fame.

- Literature and modernism: Edith Wharton, Theodore Dreiser, Theodore
  Fontane, Thomas Mann, Bertolt Brecht, Rainer Maria Rilke, Marina Tsvetaeva,
  Osip Mandelstam, Federico Garcia Lorca, Luigi Pirandello, Italo Svevo,
  Miguel de Unamuno, Soren Kierkegaard, T. S. Eliot.
- Global South literature: R. K. Narayan, Mulk Raj Anand, Tayeb Salih,
  Bessie Head, Wole Soyinka, Alejo Carpentier,
  Pablo Neruda.
- Anti-colonial and state formation: Subhas Chandra Bose, Jomo Kenyatta, Amilcar
  Cabral, Patrice Lumumba, Sukarno, Gamal Abdel Nasser, Zhou Enlai, Deng
  Xiaoping.
- Labor, social question, and reform: Jane Addams, Beatrice Webb, Sidney Webb,
  Upton Sinclair, Jacob Riis, Samuel Gompers, Eugene Debs.
- Science, systems, and environment: Nikola Tesla, James Clerk Maxwell,
  Norbert Wiener, Alan Turing, J. Robert Oppenheimer, Vannevar Bush.
- Indigenous and settler colonial witness: Chief Joseph speech tradition,
  Maori petition/treaty interpretation tradition, Aboriginal rights petition
  traditions.

Reserve substitution rule: every replacement must preserve or improve global
balance, literature centrality, source feasibility, and rights honesty. A
rights-restricted authority may stay roster-valid when its function is
essential, but it cannot be used to satisfy body-readiness claims.

## Essential Anchors

These authorities are structural anchors. Do not remove them for lane-ratio
tuning, body-rights convenience, or ordinary reserve substitution without an
explicit operator override. If a body path is blocked, keep the authority and
mark the body gate as unresolved rather than replacing the row.

### Literature and interiority anchors

Jane Austen, Mary Shelley, Dickens, Eliot, Dostoevsky, Tolstoy, Tagore, Lu Xun,
Soseki, Premchand, Machado de Assis, Rizal, Whitman, Dickinson, Melville,
Twain, Zola, Conrad, Woolf, Joyce, Kafka, Orwell, Achebe, Ngugi, Garcia
Marquez, Schreiner, Zitkala-Sa, Sembene Ousmane, Mahfouz, Hedayat, Akhmatova,
Borges.

### Political economy and social theory anchors

Marx, Engels, Mill, Tocqueville, Weber, Durkheim, Darwin, Babbage,
Nightingale, Ruskin.

### Statecraft, revolution, war, and ideology anchors

Gandhi, Nehru, Ambedkar, Sun Yat-sen, Mao, Ataturk, Lenin, Stalin / Soviet
party-state textual tradition, Luxemburg, Arendt, Hitler / Nazi textual
tradition, Churchill, Levi, Fanon, Mandela, Ho Chi Minh, Nkrumah, Garvey, UDHR
drafting tradition, United Nations Charter tradition.

### Colonized, Black Atlantic, Indigenous, and gender witness anchors

Douglass, Harriet Jacobs, Sojourner Truth textual tradition, Du Bois, Ida B.
Wells, Booker T. Washington, Cesaire, Senghor, C. L. R. James, Qiu Jin,
Simone de Beauvoir, Elizabeth Cady Stanton.

### Science, environment, and technological danger anchors

Darwin, Wallace, Faraday, Babbage, Einstein, Rachel Carson.

## Rights And Edition Triage

### Lower-risk first pass

Likely first metadata/body-research candidates are 19th-century or early
public-domain authorities with original-language or stable translation paths:
Austen, Shelley, Dickens, Douglass, Jacobs, Marx, Engels, Mill, Darwin,
Wallace, Babbage, Nightingale, Thoreau, Ruskin, Zola, Hardy, Wilde, Conrad,
Du Bois, Wells, Washington, Marti, and selected institutional texts.

### Higher-risk roster-valid candidates

Twentieth-century and translated authorities remain essential but should be
marked `body-research-incomplete` until edition, translation, source, and
jurisdiction are settled: Arendt, Levi, Fanon, Mandela, Mao, Stalin / Soviet
party-state textual tradition, Nkrumah, Sembene Ousmane, Naguib Mahfouz, Sadegh
Hedayat, Churchill, Carson,
Garcia Marquez, Achebe, Ngugi, Akhmatova, Beauvoir, Orwell, Faulkner, Joyce,
Woolf, Kafka, Borges, UDHR drafting records, and UN conference records.

### Composite traditions

These require textual-boundary handling before metadata mutation:

- Sojourner Truth speech tradition;
- Nazi textual tradition;
- Universal Declaration drafting tradition;
- United Nations Charter / San Francisco conference tradition;
- Kang Youwei and Liang Qichao reform textual tradition;
- Indigenous petition/treaty speech traditions if admitted from reserve.

## First Three Metadata Batches

Metadata batches remain proposals. They do not authorize registry mutation.

### Batch 001: Public-domain industrial literature and social witness

Target size: 12 authorities.

1. Jane Austen
2. Mary Shelley
3. Charles Dickens
4. George Eliot
5. Frederick Douglass
6. Harriet Jacobs
7. W. E. B. Du Bois
8. Herman Melville
9. Mark Twain
10. Emile Zola
11. Thomas Hardy
12. Oscar Wilde

Purpose: establish literature and testimony as the shelf spine with strong
public-domain feasibility.

### Batch 002: Political economy, labor, science, and reform

Target size: 12 authorities.

1. Karl Marx
2. Friedrich Engels
3. John Stuart Mill
4. Alexis de Tocqueville
5. Charles Darwin
6. Alfred Russel Wallace
7. Charles Babbage
8. Florence Nightingale
9. Henry David Thoreau
10. John Ruskin
11. William Morris
12. Ida B. Wells

Purpose: build the industrial system, social question, political economy, and
reform floor before harder twentieth-century rights cases.

### Batch 003: Global modernization and anti-colonial foundations

Target size: 12 authorities.

1. Jose Rizal
2. Rabindranath Tagore
3. Sun Yat-sen
4. Fukuzawa Yukichi
5. Mohandas K. Gandhi
6. B. R. Ambedkar
7. Jose Marti
8. Qiu Jin
9. Kang Youwei and Liang Qichao reform textual tradition
10. Natsume Soseki
11. Lu Xun
12. Premchand

Purpose: prevent Europe-first lock-in by establishing Asian, South Asian, and
Latin American modernization and anti-colonial witness early. Several entries
are likely `body-research-incomplete` until edition and translation rights are
settled.

## Review Pass 2026-08-23

The first review found and corrected two roster-design issues before metadata
work:

- The lane-count table originally overstated several primary-function counts.
  Counts now derive from the roster rows and sum to 96.
- The first version placed a fuzzy "Mary Wollstonecraft Shelley circle" entry
  at #81. It has been replaced by Olive Schreiner, a cleaner Industrial-era
  authority boundary that strengthens South African literary and social witness.

The review also changed Jose Rizal's primary function to
`civilization-memory-literature`, because the roster function is carried first
by anti-colonial fiction. That brings literature to 40/96 primary authorities,
meeting the architecture contract's 40 percent floor without relying on
secondary functions.

## Literature Strengthening Pass 2026-08-23

A second review raised literature closer to the architecture contract's 50
percent target without increasing the roster size. The pass replaced weaker or
harder-to-bound non-literary rows with clearer original-era literary witnesses:

- Zitkala-Sa was added in the literature-strengthening pass, strengthening
  Indigenous North American literary witness. Booker T. Washington was later
  restored in the essential-restoration pass below.
- Julius Nyerere -> Sembene Ousmane, strengthening West African literary and
  labor/decolonization memory.
- Sayyid Qutb -> Naguib Mahfouz, preserving Egypt/MENA representation through a
  stronger literary witness.
- Ali Shariati -> Sadegh Hedayat, preserving Iranian/Persian modernity through
  a cleaner literary boundary.
- George Orwell's primary function moved from `media-propaganda-public` to
  `civilization-memory-literature`, while media and propaganda remain secondary
  functions through Orwell and other political rows.

This brings primary literature to 45/96 authorities. The roster now meets the
40 percent floor and approaches the 50 percent target while improving global
literary balance.

Correction: Churchill remains essential to the Industrial shelf as a witness
to empire, wartime rhetoric, statecraft, and twentieth-century mass conflict.
He should not be removed merely to improve the literature ratio.

## Essential-Restoration Pass 2026-08-23

Booker T. Washington has been restored as an essential Industrial authority,
replacing Miguel de Unamuno, who remains a reserve literary candidate. The
reason is structural rather than reputational: Washington is a primary witness
for post-emancipation Black education, labor discipline, institutional uplift,
and the social bargain imposed inside industrial modernity. He should not have
been removed merely to improve the literature ratio.

This brings primary literature to 44/96 authorities, still above the 40 percent
floor, while strengthening the labor/social-question and Black institutional
witness lanes.

## Soviet Literary Witness Restoration 2026-08-23

Anna Akhmatova has been restored by replacing Rainer Maria Rilke, who remains
a reserve modernist-literary candidate. The substitution preserves the 44/96
literature count while strengthening Soviet-world literary witness, repression
memory, and women's testimony under revolutionary and total-war conditions.
This restoration does not reopen Churchill or Booker T. Washington.

## Russia/Soviet Lane Tuning 2026-08-23

The Russia/Soviet lane now distinguishes four functions:

- Russian literary inheritance: Pushkin, Dostoevsky, Tolstoy, Chekhov.
- Revolutionary theory and party seizure: Lenin.
- Soviet party-state power: Stalin / Soviet party-state textual tradition.
- Repression and interior witness: Akhmatova.

Stalin / Soviet party-state textual tradition replaces Soren Kierkegaard, who
moves to reserve. The reason is structural: an Industrial shelf cannot represent
the twentieth century without a source boundary for Soviet planned economy,
collectivization, terror, wartime mobilization, constitutional performance,
party reports, and Cold War state ideology. This is a harm-context and
edition-sensitive authority, not a body-ready row.

## Balance Audit 2026-08-23

The final balance audit found one accounting fault and one design caveat.

The accounting fault was that `empire-colonial-administration` was listed with
five primary authorities even though no roster row used it as a primary
function. That has been corrected to zero. Empire, colonial administration,
race, and slavery aftermath remain represented as secondary functions through
literary, war, Black Atlantic, and decolonization rows.

The corrected primary-function counts sum to 96 in both the Markdown roster and
the JSON packet. Literature remains structurally central at 43/96, above the
40 percent floor. The largest non-literary lanes are
`international-order-decolonization` at 9, `indigenous-colonized-witness` at 8,
and `mass-politics-ideology` at 7.

The regional balance is globally intentional but not symmetrical. A rough
regional grouping gives Europe 41, Asia 16, North America 15, Africa/Caribbean
8, Russia/Soviet 7, Latin America 3, International 2, and Transnational/Other
4. The main unresolved caveat is Latin America: Marti, Machado de Assis, and
Garcia Marquez provide strong coverage, but the lane may warrant one more
authority if the operator wants a more even global roster. Any such repair
should use reserve substitution rather than expanding the roster.

Reserve duplicates created by prior restoration passes were removed: admitted
authorities should not remain listed as ordinary reserve alternates.

## Latin America Tuning 2026-08-23

Jorge Luis Borges has been admitted at #95, replacing T. S. Eliot, who moves
to reserve. The substitution repairs the main balance caveat without changing
the roster size or reducing literature centrality. Borges adds a fourth Latin
American primary row and broadens the shelf beyond anti-colonial essay,
Brazilian fiction, and late twentieth-century magical-realist memory into
metaphysical modernism, encyclopedic form, translation consciousness, and
labyrinthine archive imagination.

The updated rough regional grouping is Europe 40, Asia 16, North America 15,
Africa/Caribbean 8, Russia/Soviet 7, Latin America 4, International 2, and
Transnational/Other 4. Latin America is no longer the primary balance caveat,
though it remains smaller than Europe, Asia, and North America.

## Freeze For Operator Review 2026-08-23

The roster design is frozen at 96 authorities for operator review. Further
changes should be explicit substitutions or review notes, not open-ended
roster growth. This freeze does not admit metadata, source bodies, or registry
entries; it only marks the design packet as ready for the next human review
gate.

## Acceptance Tests

- 96 authorities are present.
- Era range remains fixed at 1815-1991.
- Literature and testimony are structurally central: 43/96 primary literary
  authorities, plus several testimony and witness functions.
- Primary-function counts sum to 96 in both Markdown and JSON.
- Latin America has been tuned from 3 to 4 primary rows without expanding the
  roster.
- No registry mutation, source-body admission, download, private Archive
  ingestion, staging, commit, push, or publication occurred.
- Every candidate has a primary function, region/system, first-source target,
  and rights/edition triage.
- Rights-restricted twentieth-century authorities are roster-valid only; they
  are not body-research-ready.
- Composite traditions are identified before metadata mutation.
- The first three metadata batches are reviewable at 12 authorities each.
- `BOUNDED-HISTORICAL-SHELF-V1` remains provisional for Industrial until a
  later profile review.
