import { romanToDevanagari, devanagariToRoman, insertMatraSmartly, COMMON_MATRA_TABLETS } from "../src/lib/marathi-transliteration";

console.log("--- 1. Testing Roman to Devanagari ---");
console.log("sama-kaalee-n =>", romanToDevanagari("sama-kaalee-n"));
console.log("nat-rang =>", romanToDevanagari("nat-rang"));
console.log("sinh-gadh =>", romanToDevanagari("sinh-gadh"));
console.log("ali-baag =>", romanToDevanagari("ali-baag"));

console.log("\n--- 2. Testing Devanagari to Roman ---");
console.log("सम-कालीन =>", devanagariToRoman("सम-कालीन"));
console.log("नट-रंग =>", devanagariToRoman("नट-रंग"));

console.log("\n--- 3. Testing Smart Matra Insertion ---");
const matraAa = COMMON_MATRA_TABLETS.find(t => t.id === "matra_aa")!;
const anusvara = COMMON_MATRA_TABLETS.find(t => t.id === "anusvara")!;
const matraEe = COMMON_MATRA_TABLETS.find(t => t.id === "matra_ee")!;

// Insert 'ा' after 'सम'
let r1 = insertMatraSmartly("सम-कालीन", 2, matraAa);
console.log("Insert aa after सम: ", r1.newText, "cursor:", r1.newCursor);

// Insert 'ं' after 'स'
let r2 = insertMatraSmartly("सम-कालीन", 1, anusvara);
console.log("Insert anusvara after स: ", r2.newText, "cursor:", r2.newCursor);

// Insert matra at index 0 (should become independent vowel 'आ')
let r3 = insertMatraSmartly("कालीन", 0, matraAa);
console.log("Insert aa at index 0: ", r3.newText, "cursor:", r3.newCursor);

// Attempt double anusvara
let r4 = insertMatraSmartly("सं", 2, anusvara);
console.log("Double anusvara attempt: ", r4.newText, "notification:", r4.notification);
