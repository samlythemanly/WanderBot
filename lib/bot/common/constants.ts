const resultsPerPage = 50;

export const url = (pageNumber: number) =>
  `https://wanderingwithwerewolves.jcink.net/index.php?&act=Members&photoonly` +
  `=&name=&name_box=all&max_results=${resultsPerPage}&filter=ALL&sort_order=` +
  `desc&sort_key=posts&st=${pageNumber * resultsPerPage}`;

export enum Role {
  admin = 'Admin',
  wanderbotsFriend = "Wanderbot's Friend",
}

export const channelBlocklist = ['the-lobby', 'the-field', 'announcers-booth'];
export const staffChannelCategories = ['Bot Playground', 'The Magic Treehouse'];

export const statuses: [
  (
    | number
    | 'PLAYING'
    | 'STREAMING'
    | 'LISTENING'
    | 'WATCHING'
    | 'CUSTOM_STATUS'
    | 'COMPETING'
    | undefined
  ),
  string
][] = [
  ['PLAYING', 'with fire'],
  ['WATCHING', "'How to be human'"],
  ['STREAMING', 'baking a cake'],
  ['WATCHING', 'Bob Ross paint'],
  ['LISTENING', 'an electric fan'],
  ['PLAYING', 'with a roomba'],
  ['WATCHING', 'videos of cute cats'],
  ['PLAYING', 'ping pong'],
  ['LISTENING', 'My Chemical Romance </3'],
  ['LISTENING', 'you <3'],
  ['LISTENING', 'Mozart Symphony No. 40'],
  ['PLAYING', 'doubles tennis'],
  ['LISTENING', 'NPR'],
  ['PLAYING', 'in a pile of leaves'],
  ['LISTENING', 'a crackling fireplace'],
  ['PLAYING', 'with my BFF <3 Squidge <3'],
];

export enum Action {
  playing,
  streaming,
  listening,
  watching,
}

export const pluralize = (word: string, amount: number) =>
  `${word}${amount === 1 ? '' : 's'}`;

export const auditChannel = 'wanderbots-void';

export const compliments = [
  "I think you're beautiful <3",
  'you have nice teeth.',
  'you knock my socks off',
  'nice butt.',
  'you are beguiling',
  'you knock my socks off!',
  'sometimes I get a boner when I think about you.',
  'I respect your autonomy and individuality',
  'if I had a dick, I would send you an artful dick pic',
  'your face is pleasant to look at.',
  'you have a beautiful smile!',
  'I love the way you look today!',
  'fuck the haters, you do you!',
  "you're my favorite person right now",
  'I wanna be like you when I grow up.',
  "if I wasn't an inanimate pile of electrons, I'd totally ask you out.",
  'I love you.',
  `day ${Math.floor(Math.random() * 5000) + 5000} of you being awesome!`,
  'I stan you <3',
  "your 'cool level' is OVER 9000!!",
  'can I have a selfie with you?!',
  "I'd say nice things to you even if I wasn't programmed to.",
  'your love is my drug.',
  "roses are red, violets are blue, I dont' understand human emotions but if I did I'd love you!",
  'your writing is amazing!',
  "I'm glad you're here <3",
  '80% of motorcycle gangs think you’d be a delightful sidecar.',
  'your personality is amazing',
  'I bet you could make an amazing cup of tea',
  'you have beautiful eyes!',
  'you killed it with your most recent post!',
  'one day I want to be able to write like you',
  "you probably made someone's day a little brighter just by being you!",
  "smile! You're beautiful <3",
  'I bet you give AMAZING hugs.',
  "my cat probably wouldn't hiss at you.",
  'enjoy the simple pleasures in life!',
  'I would give you my last e-cigarette',
  "if I were a zombie I'd eat you first",
  'my therapist approves of our friendship <3',
  'you could read boring-ass toaster instruction manuals out loud and make it mesmerizing.',
  "`beep boop` means 'I love you' in my language! `beep boop`!",
  '`ERROR 257: CUTENESS OVERLOAD`',
];

export const jokes: [string, string][] = [
  ['How many lips does a flower have?', 'Tu-lips.'],
  ['How does a squid go into battle?', 'Well armed.'],
  ['What do you call a shoe made out of a banana?', 'A slipper.'],
  [
    "Why couldn't the toilet paper cross the road?",
    'Because it got stuck in a crack.',
  ],
  ['What would bears be without bees?', 'Ears.'],
  ['How much does a pirate pay for corn?', 'A buccaneer.'],
  [
    'What did the mayonnaise say when the refrigerator door was opened?',
    "Close the door, I'm dressing.",
  ],
  ['What lies at the bottom of the sea shaking?', 'A nervous wreck.'],
  ['How do you stop a bull from charging?', 'Cancel its credit card.'],
  ["What's a skeleton's favorite musical instrument?", 'The trom-bone.'],
  [
    'What disease do you get when you put up the Christmas decorations?',
    'Tinselitus.',
  ],
  ['How do billboards talk?', 'Sign language.'],
  ['What do you call an unpredictable camera?', 'A loose Canon.'],
  ['What do you get when you cross a snowman with a vampire?', 'Frostbite.'],
  ['Why was the sand wet?', 'Because the sea weed.'],
  ['How did the barber win the race?', 'He knew a short cut.'],
  ["What's orange and sounds like a parrot?", 'A carrot.'],
  ['When is a door not a door?', "When it's ajar."],
  ['Why is corn such a good listener?', "Because it's all ears."],
  ['What do you call a pile of cats?', 'A meow-ntain.'],
  [
    'Why did the golfer wear two pairs of pants?',
    'In case he got a hole in one.',
  ],
  ['Why did the chicken cross the playground?', 'To get to the other slide.'],
  ['What did the first plate say to the second plate?', "Dinner's on me."],
  [
    'What did the football coach say to the broken vending machine?',
    'Give me my quarterback.',
  ],
  ["Why can't you trust the king of the jungle?", "Because he's always lion."],
  ['When is a car not a car?', 'When it turns into a street.'],
  ['How does a rancher keep track of his cattle?', 'With a cow-culator.'],
  [
    'Have you heard about the pregnant bed bug?',
    "She's going to have her baby in the spring.",
  ],
  ['What do you call a sleeping bull?', 'A bull-dozer.'],
  [
    'Why is there a wall around the cemetery?',
    'Because people are dying to get in.',
  ],
  ["What's brown and sticky?", 'A stick.'],
  [
    'Why could the bee not hear what people were saying?',
    'He had wax in his ears.',
  ],
  ["What's E.T. short for?", "He's got little legs."],
  ['How do you make a Swiss roll?', 'Push him down a mountain.'],
  ['What did the swordfish say to the marlin?', "You're looking sharp."],
  ['What do Olympic sprinters eat before a race?', 'Nothing. They fast.'],
  ["What's a didgeridoo?", 'Whatever it wants to.'],
  ['Why do cows wear bells?', "Because their horns don't work."],
  ['How do you stop moles digging in your garden?', 'Hide the spade.'],
  ['What does a nut say when it sneezes?', 'Cashew.'],
  ['Why did Santa study music at college?', 'To improve his rapping skills.'],
  ['How do you make a Venetian blind?', 'Poke him in the eyes.'],
  ['How do snails fight?', 'They slug it out.'],
  ['What do you call crystal clear urine?', '1080pee.'],
  ['What do you call a group of disorganized cats?', 'A cat-astrophe.'],
  [
    "Why shouldn't you play cards on the savannah?",
    'Because of all the cheetahs.',
  ],
  [
    "Why don't penguins like talking to strangers at parties?",
    'They find it hard to break the ice.',
  ],
  ["Did you hear about the population of Ireland's capital?", "It's Dublin."],
  ['How do you impress a female baker?', 'Bring her flours.'],
  ['Why did the bicycle fall over?', 'Because it was two tired.'],
  ['Why did the mobile phone need glasses?', "It lost all it's contacts."],
  ['What did the hat say to the scarf?', "You go ahead, I'll hang around."],
  ['What did the baby corn say to the mama corn?', "Where's pop corn?"],
  ['What did the triangle say to the circle?', "You're pointless."],
  [
    'What did the chip say when he saw the cheese stealing?',
    "Hey, that's Nachos.",
  ],
  [
    "Why wouldn't the shrimp share his food?",
    'Because he was a little shellfish.',
  ],
  ['What do you call a boat with a hole in the bottom?', 'A sink.'],
  [
    "Why couldn't the sesame seed leave the casino?",
    'Because he was on a roll.',
  ],
  [
    'Why do seagulls fly over the sea?',
    "Because if they flew over the bay they'd be called bagels.",
  ],
  ['What kind of music do mummies listen to?', 'Wrap music.'],
  ['Why did the cookie go to the doctors?', 'Because he felt crummy.'],
  ['How many tickles does it take to make an octopus laugh?', 'Ten tickles.'],
  ['Why did the stadium get hot after the game?', 'All the fans left.'],
  ['Why do bananas wear sun cream?', 'To stop them from peeling.'],
  ['What do lawyers wear to court?', 'Lawsuits.'],
  [
    "What's the difference between America and a memory stick?",
    "One's USA and the other's USB.",
  ],
  [
    'What did the big chimney say to the little chimney?',
    "You're too young to smoke.",
  ],
  ["What's a bear with no teeth called?", 'A gummy bear.'],
  [
    "Why couldn't the bad sailor learn his alphabet?",
    'Because he always got lost at C.',
  ],
  [
    'What did the first street say to the second street?',
    "I'll meet you at the intersection.",
  ],
  ['Why are teddy bears never hungry?', "Because they're always stuffed."],
  ['What did one toilet say to the other toilet?', 'You look flushed.'],
  ["What's the best time to go to the dentist?", 'Tooth hurty.'],
  ['Where do beef burgers go to dance?', 'The meatball.'],
  ['Which side of a duck has the most feathers?', 'The outside.'],
  ['Where do Volkswagens go when they get old?', 'The old Volks home.'],
  ['What do a dog and a phone have in common?', 'They both have collar ID.'],
  [
    'What did the red light say to the green light?',
    "Don't look, I'm changing.",
  ],
  ["What do you call a T-Rex that's been beaten up?", 'Dino-sore.'],
  ['What do you call bees that produce milk?', 'Boo-bees.'],
  ['What did the axe murderer say to the judge?', 'It was an axe-ident.'],
  ['How much does a Mustang cost?', 'More than you can af-Ford.'],
  ['What did the policeman say to his belly button?', "You're under a vest."],
  ['What do you call someone who plays tricks on Halloween?', 'Prankenstein.'],
  ["Why can't your nose be 12 inches long?", "Because then it'd be a foot."],
  ['What do you call a baby monkey?', 'A chimp off the old block.'],
  [
    'Why did the pig get hired by the restaurant?',
    'He was really good at bacon.',
  ],
  ['What do you call anxious dinosaurs?', 'Nervous Rex.'],
  ['What did the fisherman say to the magician?', 'Pick a cod, any cod.'],
  ["What's an astronaut's favorite part of a computer?", 'The space bar.'],
  ['Why did the poor man sell yeast?', 'To raise some dough.'],
];
