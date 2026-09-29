/**
 * Sportsbook Odds Tracker
 * Google Apps Script to fetch betting lines from Novig, DraftKings, FanDuel, Caesars, MGM, and Fanatics
 * uses The Odds API (https://the-odds-api.com/) and Novig's Developer API
 */

// Custom Menu on Sheet Open
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('Sportsbook Tracker')
      .addItem('Refresh Odds Data', 'updateOdds')
      .addItem('Toggle Auto-Updates (Every 4 Hours)', 'toggleAutoUpdate')
      .addItem('Setup Sheets (First Time)', 'setupSheets')
      .addToUi();
}

/**
 * Automatically sets up the spreadsheet with settings, data, and market depth sheets.
 */
function setupSheets() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. Create or verify "Settings" Sheet
  var settingsSheet = ss.getSheetByName("Settings");
  if (!settingsSheet) {
    settingsSheet = ss.insertSheet("Settings");
    
    // Formatting Settings Sheet
    settingsSheet.getRange("A1:B1").setValues([["Parameter", "Value"]]).setFontWeight("bold").setBackground("#f3f3f3");
    
    var defaultSettings = [
      ["The Odds API Key", "ea94f855768fa6bf4fbdc4f60074ed11"],
      ["Novig Client ID (Optional)", ""],
      ["Novig Client Secret (Optional)", ""],
      ["Odds Format (american or decimal)", "american"],
      ["Include Novig (Exchange)", true],
      ["Include DraftKings", true],
      ["Include FanDuel", true],
      ["Include BetMGM", true],
      ["Include Caesars (Requires Paid API Tier)", true],
      ["Include Fanatics (Requires Paid API Tier)", true],
      ["--- ACTIVE SPORTS ---", ""],
      ["NFL (americanfootball_nfl)", true],
      ["NCAAF (americanfootball_ncaaf)", true],
      ["NBA (basketball_nba)", false],
      ["NCAAB (basketball_ncaab)", false],
      ["WNBA (basketball_wnba)", true],
      ["NCAAW Basketball (basketball_wncaab)", false],
      ["MLB (baseball_mlb)", true],
      ["NHL (icehockey_nhl)", false],
      ["Tennis (all active tournaments)", true],
      ["--- STATUS ---", ""],
      ["Last Updated", ""],
      ["Status Message", "Click 'Sportsbook Tracker' -> 'Refresh Odds Data' to begin!"]
    ];
    
    settingsSheet.getRange(2, 1, defaultSettings.length, 2).setValues(defaultSettings);
    
    // Add checkboxes for boolean settings
    var checkboxRanges = [
      "B6", "B7", "B8", "B9", "B10", "B11", // Bookmakers
      "B13", "B14", "B15", "B16", "B17", "B18", "B19", "B20", "B21" // Sports
    ];
    checkboxRanges.forEach(function(cell) {
      settingsSheet.getRange(cell).insertCheckboxes();
    });
    
    settingsSheet.getRange("A12:B12").setFontWeight("bold").setBackground("#e6effa");
    settingsSheet.getRange("A22:B22").setFontWeight("bold").setBackground("#e6effa");
    
    settingsSheet.autoResizeColumn(1);
    settingsSheet.autoResizeColumn(2);
  }
  
  // 2. Create or verify "Odds Data" Sheet
  var dataSheet = ss.getSheetByName("Odds Data");
  if (!dataSheet) {
    dataSheet = ss.insertSheet("Odds Data");
    var headers = [[
      "Event ID", 
      "Sport", 
      "Commence Time (UTC)", 
      "Home Team", 
      "Away Team", 
      "Bookmaker", 
      "Market", 
      "Outcome", 
      "Point", 
      "Price", 
      "Last Update (UTC)",
      "Liquidity (USD)"
    ]];
    dataSheet.getRange(1, 1, 1, headers[0].length).setValues(headers).setFontWeight("bold").setBackground("#e2efda");
    dataSheet.autoResizeColumns(1, headers[0].length);
  }
  
  // 3. Create or verify "Novig Market Depth" Sheet
  var depthSheet = ss.getSheetByName("Novig Market Depth");
  if (!depthSheet) {
    depthSheet = ss.insertSheet("Novig Market Depth");
    var depthHeaders = [[
      "Event Name", 
      "Sport", 
      "Market Type", 
      "Outcome Name", 
      "Line", 
      "Side", 
      "Odds", 
      "Max Bet Size (Liquidity)", 
      "Depth Level",
      "Outcome Class"
    ]];
    depthSheet.getRange(1, 1, 1, depthHeaders[0].length).setValues(depthHeaders).setFontWeight("bold").setBackground("#d9e1f2");
    depthSheet.autoResizeColumns(1, depthHeaders[0].length);
  }
  
  SpreadsheetApp.getUi().alert("Setup completed successfully! Please enter your Novig API keys on the Settings sheet to enable detailed order book and liquidity depth tracking.");
}

/**
 * Main function to fetch odds data from The Odds API and write it to the sheet.
 */
function updateOdds() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var settingsSheet = ss.getSheetByName("Settings");
  
  if (!settingsSheet) {
    setupSheets();
    settingsSheet = ss.getSheetByName("Settings");
  }
  
  // Dynamic Settings Reader
  var settings = readSettings(settingsSheet);
  var apiKey = settings["The Odds API Key"] ? settings["The Odds API Key"].toString().trim() : "";
  var oddsFormat = settings["Odds Format (american or decimal)"] ? settings["Odds Format (american or decimal)"].toString().trim() : "american";
  
  if (!apiKey) {
    updateStatus("Error: The Odds API Key is missing. Please enter it in the Settings sheet.", settingsSheet);
    return;
  }
  
  // Get active bookmaker keys
  var enabledBooks = [];
  if (settings["Include Novig (Exchange)"] === true) enabledBooks.push("novig");
  if (settings["Include DraftKings"] === true) enabledBooks.push("draftkings");
  if (settings["Include FanDuel"] === true) enabledBooks.push("fanduel");
  if (settings["Include BetMGM"] === true) enabledBooks.push("betmgm");
  if (settings["Include Caesars (Requires Paid API Tier)"] === true) enabledBooks.push("williamhill_us");
  if (settings["Include Fanatics (Requires Paid API Tier)"] === true) enabledBooks.push("fanatics");
  if (settings["Include BetRivers"] === true) enabledBooks.push("betrivers");
  
  if (enabledBooks.length === 0) {
    updateStatus("Error: No bookmakers selected. Check at least one bookmaker.", settingsSheet);
    return;
  }
  
  // Define sport keys mapping from configuration names
  var sportsToQuery = [];
  if (settings["NFL (americanfootball_nfl)"] === true) sportsToQuery.push("americanfootball_nfl");
  if (settings["NCAAF (americanfootball_ncaaf)"] === true) sportsToQuery.push("americanfootball_ncaaf");
  if (settings["NBA (basketball_nba)"] === true) sportsToQuery.push("basketball_nba");
  if (settings["NCAAB (basketball_ncaab)"] === true) sportsToQuery.push("basketball_ncaab");
  if (settings["WNBA (basketball_wnba)"] === true) sportsToQuery.push("basketball_wnba");
  if (settings["NCAAW Basketball (basketball_wncaab)"] === true) sportsToQuery.push("basketball_wncaab");
  if (settings["MLB (baseball_mlb)"] === true) sportsToQuery.push("baseball_mlb");
  if (settings["NHL (icehockey_nhl)"] === true) sportsToQuery.push("icehockey_nhl");
  
  // Dynamic Tennis tourney checking
  if (settings["Tennis (all active tournaments)"] === true) {
    updateStatus("Scanning active tennis tournaments...", settingsSheet);
    var activeTennisSports = getActiveTennisSports(apiKey);
    sportsToQuery = sportsToQuery.concat(activeTennisSports);
  }
  
  if (sportsToQuery.length === 0) {
    updateStatus("Error: No sports selected. Check at least one sport in the Settings sheet.", settingsSheet);
    return;
  }
  
  updateStatus("Refreshing odds... Please wait...", settingsSheet);
  
  var oddsRows = [];
  var errors = [];
  
  // To fetch Novig, we need the 'us_ex' region. For other books, we need the 'us' region.
  var regions = "us";
  if (enabledBooks.indexOf("novig") !== -1) {
    regions = "us,us_ex";
  }
  
  sportsToQuery.forEach(function(sportKey) {
    try {
      var url = "https://api.the-odds-api.com/v4/sports/" + sportKey + "/odds/" +
                "?apiKey=" + apiKey +
                "&regions=" + regions +
                "&markets=h2h,spreads,totals" +
                "&oddsFormat=" + oddsFormat +
                "&bookmakers=" + enabledBooks.join(",");
      
      var response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
      var responseCode = response.getResponseCode();
      var responseText = response.getContentText();
      
      if (responseCode !== 200) {
        var errorMsg = "API returned error " + responseCode + " for " + sportKey;
        try {
          var errorObj = JSON.parse(responseText);
          if (errorObj.message) errorMsg += ": " + errorObj.message;
        } catch (e) {}
        errors.push(errorMsg);
        return;
      }
      
      var data = JSON.parse(responseText);
      
      data.forEach(function(event) {
        var eventId = event.id;
        var sportTitle = event.sport_title;
        var commenceTime = event.commence_time;
        var homeTeam = event.home_team;
        var awayTeam = event.away_team;
        
        event.bookmakers.forEach(function(bookmaker) {
          var bookmakerTitle = bookmaker.title;
          var lastUpdate = bookmaker.last_update;
          
          bookmaker.markets.forEach(function(market) {
            var marketKey = market.key; // h2h, spreads, totals
            
            market.outcomes.forEach(function(outcome) {
              var outcomeName = outcome.name;
              var price = outcome.price;
              var point = outcome.point !== undefined ? outcome.point : "";
              
              oddsRows.push([
                eventId,
                sportTitle,
                commenceTime,
                homeTeam,
                awayTeam,
                bookmakerTitle,
                marketKey,
                outcomeName,
                point,
                price,
                lastUpdate
              ]);
            });
          });
        });
      });
      
    } catch (e) {
      errors.push("Failed to fetch " + sportKey + ": " + e.message);
    }
  });
  
  // Write data to "Odds Data" sheet
  var dataSheet = ss.getSheetByName("Odds Data");
  if (!dataSheet) {
    setupSheets();
    dataSheet = ss.getSheetByName("Odds Data");
  }
  
  // Clear existing content below headers
  var lastRow = dataSheet.getLastRow();
  if (lastRow > 1) {
    dataSheet.getRange(2, 1, lastRow - 1, dataSheet.getLastColumn()).clearContent();
  }
  
  // Write new content
  if (oddsRows.length > 0) {
    dataSheet.getRange(2, 1, oddsRows.length, oddsRows[0].length).setValues(oddsRows);
    dataSheet.autoResizeColumns(1, oddsRows[0].length);
  }
  
  // Fetch detailed Novig order book depth if credentials are provided
  var novigClientId = settings["Novig Client ID (Optional)"] ? settings["Novig Client ID (Optional)"].toString().trim() : "";
  var novigClientSecret = settings["Novig Client Secret (Optional)"] ? settings["Novig Client Secret (Optional)"].toString().trim() : "";
  
  if (novigClientId && novigClientSecret) {
    updateStatus("Fetching detailed Novig order books...", settingsSheet);
    updateNovigDepth(novigClientId, novigClientSecret, sportsToQuery, oddsFormat);
  } else {
    // Clear depth sheet and set status if keys missing
    var depthSheet = ss.getSheetByName("Novig Market Depth");
    if (depthSheet) {
      var depthLastRow = depthSheet.getLastRow();
      if (depthLastRow > 1) {
        depthSheet.getRange(2, 1, depthLastRow - 1, depthSheet.getLastColumn()).clearContent();
      }
      depthSheet.getRange("A2").setValue("To view detailed Novig order book depth and liquidity, please enter your Novig Client ID and Client Secret in the Settings sheet.");
    }
  }
  
  // Final Status Update
  var statusText = "Successfully updated " + oddsRows.length + " lines of odds.";
  if (errors.length > 0) {
    statusText += " Errors encountered: " + errors.join(" | ");
  }
  
  updateStatus(statusText, settingsSheet);
}

/**
 * Reads settings key-values from Settings worksheet dynamically.
 */
function readSettings(settingsSheet) {
  var values = settingsSheet.getRange(1, 1, settingsSheet.getLastRow(), 2).getValues();
  var settings = {};
  for (var i = 0; i < values.length; i++) {
    var key = values[i][0];
    var val = values[i][1];
    if (key) {
      settings[key.toString().trim()] = val;
    }
  }
  return settings;
}

/**
 * Queries the list of currently in-season sports to find all active tennis keys.
 */
function getActiveTennisSports(apiKey) {
  var tennisSports = [];
  try {
    var url = "https://api.the-odds-api.com/v4/sports/?apiKey=" + apiKey;
    var response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    if (response.getResponseCode() === 200) {
      var sports = JSON.parse(response.getContentText());
      sports.forEach(function(sport) {
        if (sport.key.indexOf("tennis_") === 0) {
          tennisSports.push(sport.key);
        }
      });
    }
  } catch (e) {
    Logger.log("Failed to fetch active tennis tournaments: " + e.message);
  }
  return tennisSports;
}

/**
 * Authenticates with Novig using Client Credentials.
 */
function getNovigToken(clientId, clientSecret) {
  var url = "https://api.novig.us/nbx/v1/auth/emm-token";
  var payload = {
    "grant_type": "client_credentials",
    "client_id": clientId,
    "client_secret": clientSecret
  };
  
  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  var response = UrlFetchApp.fetch(url, options);
  if (response.getResponseCode() === 200) {
    var data = JSON.parse(response.getContentText());
    return data.access_token;
  } else {
    throw new Error("Novig Authentication failed: " + response.getContentText());
  }
}

/**
 * Fetches order book depth from Novig REST API for active sports.
 */
function updateNovigDepth(clientId, clientSecret, sportsToQuery, oddsFormat) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var depthSheet = ss.getSheetByName("Novig Market Depth");
  
  if (!depthSheet) {
    setupSheets();
    depthSheet = ss.getSheetByName("Novig Market Depth");
  }
  
  try {
    var token = getNovigToken(clientId, clientSecret);
    
    // Fetch active markets from Novig
    var marketsUrl = "https://api.novig.us/nbx/v2/markets";
    var options = {
      "method": "get",
      "headers": { "Authorization": "Bearer " + token },
      "muteHttpExceptions": true
    };
    
    var response = UrlFetchApp.fetch(marketsUrl, options);
    if (response.getResponseCode() !== 200) {
      depthSheet.getRange("A2").setValue("Error fetching Novig markets: " + response.getContentText());
      return;
    }
    
    var markets = JSON.parse(response.getContentText());
    var depthRows = [];
    
    // Safety limit to avoid script timeouts (Apps Script 6min limit)
    var maxMarketsToFetch = 30;
    var fetchedCount = 0;
    
    for (var i = 0; i < markets.length; i++) {
      if (fetchedCount >= maxMarketsToFetch) break;
      var market = markets[i];
      
      // Standardize sport naming comparisons (case insensitive)
      var sportKey = market.sport ? market.sport.toLowerCase() : "";
      var matched = false;
      sportsToQuery.forEach(function(activeSport) {
        if (activeSport.indexOf(sportKey) !== -1 || sportKey.indexOf(activeSport) !== -1) {
          matched = true;
        }
      });
      
      if (!matched) continue;
      
      var marketId = market.id;
      var eventName = market.event_name || ((market.home_team || "Team A") + " vs " + (market.away_team || "Team B"));
      var marketType = market.market_type || "";
      var line = market.line !== undefined ? market.line : "";
      
      // Fetch the orderbook for this specific market
      var bookUrl = "https://api.novig.us/nbx/v2/book/" + marketId;
      var bookResponse = UrlFetchApp.fetch(bookUrl, options);
      
      if (bookResponse.getResponseCode() === 200) {
        var book = JSON.parse(bookResponse.getContentText());
        fetchedCount++;
        
        if (book.outcomes) {
          Object.keys(book.outcomes).forEach(function(outcomeId) {
            var outcomeData = book.outcomes[outcomeId];
            
            // Resolve outcome name
            var outcomeName = outcomeId;
            if (market.outcomes) {
              var found = market.outcomes.find(function(o) { return o.id === outcomeId; });
              if (found) outcomeName = found.name;
            }
            
            // Parse Bids (Backing orders - odds you bet against or match)
            if (outcomeData.bids) {
              outcomeData.bids.forEach(function(bid, index) {
                if (index >= 3) return; // Keep top 3 levels of depth
                var odds = probToAmerican(bid.price, oddsFormat);
                var maxBetRisk = (bid.qty / 100) * bid.price;
                depthRows.push([
                  eventName,
                  market.sport || "",
                  marketType,
                  outcomeName,
                  line,
                  "Back",
                  odds,
                  maxBetRisk.toFixed(2),
                  (index + 1)
                ]);
              });
            }
            
            // Parse Asks (Laying orders - odds you bet on or match)
            if (outcomeData.asks) {
              outcomeData.asks.forEach(function(ask, index) {
                if (index >= 3) return; // Keep top 3 levels of depth
                var odds = probToAmerican(1 - ask.price, oddsFormat);
                var maxBetRisk = (ask.qty / 100) * (1 - ask.price);
                depthRows.push([
                  eventName,
                  market.sport || "",
                  marketType,
                  outcomeName,
                  line,
                  "Lay",
                  odds,
                  maxBetRisk.toFixed(2),
                  (index + 1)
                ]);
              });
            }
          });
        }
      }
    }
    
    // Clear and write the database-style depth rows
    var depthLastRow = depthSheet.getLastRow();
    if (depthLastRow > 1) {
      depthSheet.getRange(2, 1, depthLastRow - 1, depthSheet.getLastColumn()).clearContent();
    }
    
    if (depthRows.length > 0) {
      depthSheet.getRange(2, 1, depthRows.length, depthRows[0].length).setValues(depthRows);
      depthSheet.autoResizeColumns(1, depthRows[0].length);
    } else {
      depthSheet.getRange("A2").setValue("No active Novig markets found matching your active sports selection.");
    }
    
  } catch (e) {
    depthSheet.getRange("A2").setValue("Failed to parse Novig depth: " + e.message);
  }
}

/**
 * Converts internal Novig decimal probabilities (e.g. 0.5238) to American/Decimal Odds.
 */
function probToAmerican(prob, format) {
  if (!prob || prob <= 0 || prob >= 1) return "";
  
  if (format === "decimal") {
    return (1 / prob).toFixed(2);
  }
  
  // American odds conversion
  if (prob > 0.5) {
    var odds = -(prob / (1 - prob)) * 100;
    return Math.round(odds);
  } else {
    var odds = ((1 - prob) / prob) * 100;
    return "+" + Math.round(odds);
  }
}

/**
 * Toggles the background hourly auto-update trigger on and off.
 */
function toggleAutoUpdate() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var settingsSheet = ss.getSheetByName("Settings");
  if (!settingsSheet) {
    setupSheets();
    settingsSheet = ss.getSheetByName("Settings");
  }

  var triggers = ScriptApp.getProjectTriggers();
  var triggerExists = false;
  var targetTrigger = null;

  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'updateOdds') {
      triggerExists = true;
      targetTrigger = triggers[i];
      break;
    }
  }

  if (triggerExists) {
    ScriptApp.deleteTrigger(targetTrigger);
    updateStatus("Auto-updates disabled.", settingsSheet);
    SpreadsheetApp.getUi().alert("Auto-updates disabled. The odds will now only refresh when you manually click 'Refresh Odds Data'.");
  } else {
    // Create a time-driven trigger to run every 4 hours
    ScriptApp.newTrigger('updateOdds')
        .timeBased()
        .everyHours(4)
        .create();
    updateStatus("Auto-updates enabled (running every 4 hours).", settingsSheet);
    SpreadsheetApp.getUi().alert("Auto-updates enabled! The script will automatically fetch new odds every 4 hours in the background.");
  }
}

/**
 * Helper to update status message and timestamp on Settings sheet.
 */
function updateStatus(message, settingsSheet) {
  var timestamp = Utilities.formatDate(new Date(), "America/New_York", "yyyy-MM-dd hh:mm:ss a 'ET'");
  settingsSheet.getRange("B23").setValue(timestamp);
  settingsSheet.getRange("B24").setValue(message);
  SpreadsheetApp.flush();
}

/**
 * Serves live odds and player props as JSON for the OddsHub Mobile App.
 * To enable on your mobile phone:
 * In Apps Script editor -> Deploy -> New deployment -> Select type: Web app
 * -> Execute as: Me -> Who has access: Anyone
 * Copy the URL and paste it into the OddsHub Mobile Settings modal!
 */
function doGet(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var oddsSheet = ss.getSheetByName("Odds Data");
  var propsSheet = ss.getSheetByName("Player Props Data");
  
  var oddsRows = oddsSheet ? oddsSheet.getDataRange().getValues() : [];
  var propsRows = propsSheet ? propsSheet.getDataRange().getValues() : [];
  
  // Return simple JSON feed
  var result = {
    updated_at: Utilities.formatDate(new Date(), "America/New_York", "yyyy-MM-dd hh:mm:ss a 'ET'"),
    odds: oddsRows,
    props: propsRows
  };
  
  return ContentService.createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}
