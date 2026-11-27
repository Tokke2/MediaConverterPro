# Regler för MediaForge

Dessa regler gäller framtida arbete i detta repo, i den mån de är förenliga med överordnade instruktioner och faktisk åtkomst. Anpassa villkorliga krav till den aktuella appen; hitta inte på funktioner som inte finns.

## Arbetsflöde och release — hårda regler

- Arbeta endast på den arbetsgren som sessionen anger; arbeta aldrig mot eller pusha till `main`. Byt, skapa, byt namn på eller radera inte grenar på eget initiativ. Sessionens gren kan styras av plattformen och kan inte garanteras vara densamma i en ny chatt. Ingen merge eller PR.
- Vid varje kodändring: kör relevanta tester och uppdatera GitHub-release `0.0.2`, dess tagg och releaseanteckningar; markera den som Latest. Behåll versionen tills användaren säger annat. Om ett steg misslyckas, rapportera det.
- Uppdateraren ska jämföra appfiler, skydda användardata och lokala ändringar och inte ändra `main`, slå samman grenar eller tyst byta gren. Verifiera resultat, behåll återställning vid fel och ta bort uppdateringens backup först efter verifierad framgång. Starta om automatiskt efter lyckad uppdatering.
- Nya instruktioner märkta `regel` eller `hård regel` ska dokumenteras här och publiceras på den tillåtna arbetsgrenen. Ändra inte repo-inställningar eller andra grenar utan nödvändig behörighet och tillåtelse.
- Undvik tysta beroende- och gränssnittsbrott. Kör relevanta tester före leverans; redovisa plattformsbegränsningar och det som inte testats.

## Återkommande användarönskemål

- Vid begäran om idéer: skriv 25 nya förslag i chatten. Efter 10 chattmeddelanden: skriv en ny lista med 10 ej återanvända idéer i chatten. Saknar agenten historik för att kontrollera antalet eller tidigare idéer ska det anges, inte gissas. Påstå inte att konkurrenter saknar något eller att efterfrågan finns utan underlag.
- Anpassa layout, fönsterbredd och höjd till skärmstorlek och DPI, ge tydlig text, bilder och tabeller, minimera onödig scroll och använd genomgående skarp, redigerbar vektorlogotyp samt konsekventa ikoner. Starta minimerat utan terminalfönster; visa fönstret med maximal tillgänglig höjd när det återställs.
- Sträva efter tydligare, icke grumlig skärpa och lägre minnes-, energi- och tidsåtgång utan att lova mätbar förbättring utan mätning.
- För appar som faktiskt har profiler: separat inställningsflik för att skapa profiler. Återställ ruteval i projektskapare endast om den aktuella appen tidigare hade detta i sin ttk-version.
- Planera automatisk uppdatering kl. 00:00 lokal tid och återuppta missade kontroller när appen är igång igen. Avbryt inte pågående jobb och starta om efter lyckad uppdatering.
- Arkivera gårdagens applogg och radera arkiverade loggar efter sju dagar. Behåll komplett fellogg samt möjlighet att markera åtgärdade fel; radera inte tyst historik utan säker identifiering av vad som är åtgärdat.
- Om appen har tabeller ska kolumner där det är säkert kunna sorteras och flyttas utan att data eller åtgärder kopplas fel.
