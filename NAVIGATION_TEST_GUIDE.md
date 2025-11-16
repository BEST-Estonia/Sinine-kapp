╔══════════════════════════════════════════════════════════════════════════════╗
║               NAVIGATION & SCREEN FLOW MANUAL TEST GUIDE                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

This guide tests the stack-based ScreenManager implementation to ensure
correct screen ordering, navigation flows, and lifecycle management.

PREREQUISITES:
--------------
1. Install dependencies: pip install -r requirements.txt
2. Navigate to src directory: cd src
3. Run the application: python main.py

═══════════════════════════════════════════════════════════════════════════════
TEST 1: BORROW FLOW (Open Doors → Card Scan → QR Scan → Basket → Thank You)
═══════════════════════════════════════════════════════════════════════════════

1. Start app → Main Menu visible (Sneaky visible at bottom)

2. Tap "Open Doors" button
   Expected: Card Scan screen appears with message "Please swipe your ID card"
   
3. In console, enter card ID: 1 (registered admin user)
   Expected: "Welcome, Admin User!" message appears
   Expected: QR Scan screen appears in borrow mode
   
4. Tap "Scan Item" button
   In console, enter QR code: 1
   Expected: Item "Coca Cola" added to basket
   Expected: Basket shows "1 items"
   
5. Tap "Scan Item" button again
   In console, enter QR code: 2
   Expected: Item "Sprite" added to basket
   Expected: Basket shows "2 items"
   
6. Tap "Done" button
   Expected: Basket confirmation screen appears
   Expected: Shows "Total: 2 items"
   Expected: Shows both Coca Cola and Sprite with quantities
   
7. Tap "Confirm" button
   Expected: Thank You screen appears
   Expected: Shows "You borrowed 2 item(s)"
   Expected: Shows "Please close the doors"
   Expected: Shows due date
   Expected: Lists items borrowed
   
8. Tap "OK" button (or wait 6 seconds for auto-return)
   Expected: Returns to Main Menu
   Expected: Screen stack is cleared

PASS CRITERIA:
- ✓ Only one screen visible at a time (correct Z-order)
- ✓ Navigation flows in correct order
- ✓ Back button on any screen returns to previous screen
- ✓ Sneaky character visible at bottom on all screens
- ✓ Thank You screen returns to Main Menu (go_to, not push)

═══════════════════════════════════════════════════════════════════════════════
TEST 2: RETURN FLOW (Return Drink → Card Scan → QR Scan → Basket → Thank You)
═══════════════════════════════════════════════════════════════════════════════

1. Start at Main Menu

2. Tap "Return Drink" button
   Expected: Card Scan screen appears
   
3. In console, enter card ID: 2 (registered non-admin user)
   Expected: "Welcome, Alice Johnson!" message appears
   Expected: QR Scan screen appears in return mode
   Expected: Title shows "Return Items"
   
4. Tap "Scan Item" button
   In console, enter QR code: 1
   Expected: Item added to basket
   
5. Tap "Done" button
   Expected: Basket confirmation screen appears
   Expected: Title shows "Confirm Return"
   
6. Tap "Confirm" button
   Expected: Thank You screen appears
   Expected: Shows "You returned X item(s)"
   Expected: Shows "Thank you for returning!"
   Expected: NO due date shown (returns don't have due dates)
   
7. Tap "OK" button
   Expected: Returns to Main Menu

PASS CRITERIA:
- ✓ Return flow uses same screens as borrow but with different modes
- ✓ Correct titles and messages for return action
- ✓ No due date shown in Thank You screen for returns

═══════════════════════════════════════════════════════════════════════════════
TEST 3: ADMIN ACCESS - AUTHORIZED (user_id == 1)
═══════════════════════════════════════════════════════════════════════════════

1. Start at Main Menu

2. Tap "Admin Panel" button
   Expected: Card Scan screen appears
   
3. In console, enter card ID: 1 (Admin User, user_id == 1)
   Expected: "Welcome, Admin User!" message appears
   Expected: Admin Main screen appears
   Expected: Shows "Admin: Admin User"
   Expected: Shows 3 buttons: "Users List", "Inventory Manager", "System Logs"
   
4. Tap "Users List" button
   Expected: Admin Users screen appears
   Expected: Shows list of registered users
   
5. Tap "← Back" button
   Expected: Returns to Admin Main screen
   
6. Tap "← Back" button again
   Expected: Returns to Card Scan screen
   
7. Tap "← Back" button again
   Expected: Returns to Main Menu

PASS CRITERIA:
- ✓ Admin user (ID 1) can access admin panel
- ✓ Navigation through admin screens works correctly
- ✓ Back button pops screens in correct order

═══════════════════════════════════════════════════════════════════════════════
TEST 4: ADMIN ACCESS - DENIED (user_id != 1)
═══════════════════════════════════════════════════════════════════════════════

1. Start at Main Menu

2. Tap "Admin Panel" button
   Expected: Card Scan screen appears
   
3. In console, enter card ID: 2 (Alice Johnson, user_id == 2, not admin)
   Expected: "Access Denied! Only admin (user ID 1) can access." message appears
   Expected: Wait 2 seconds
   Expected: Automatically returns to Main Menu (via screen_manager.pop())
   
PASS CRITERIA:
- ✓ Non-admin users (user_id != 1) are denied admin access
- ✓ Access Denied message is shown clearly
- ✓ Automatically returns to Main Menu after showing message
- ✓ Does NOT proceed to Admin Main screen

═══════════════════════════════════════════════════════════════════════════════
TEST 5: UNREGISTERED CARD → REGISTRATION → CONTINUE FLOW
═══════════════════════════════════════════════════════════════════════════════

1. Start at Main Menu

2. Tap "Open Doors" button
   Expected: Card Scan screen appears
   
3. In console, enter card ID: 999 (unregistered)
   Expected: "Card 999 not registered." message appears
   Expected: Wait 0.8 seconds
   Expected: Register User screen appears
   Expected: Shows "Card 999 is not registered."
   Expected: Input box for entering name
   Expected: On-screen keyboard visible
   
4. Using on-screen keyboard, enter name: "Test User"
   
5. Tap "Register" button
   Expected: "Welcome, Test User! Registration successful." message appears
   Expected: Wait 1.5 seconds
   Expected: Register screen is popped
   Expected: QR Scan screen is pushed for borrow action
   Expected: Shows "Borrow Items" screen
   Expected: User can now scan items
   
6. Tap "← Back" button
   Expected: Returns to Main Menu (all screens popped)
   
7. Restart flow to verify registration persisted:
   Tap "Open Doors", enter card 999
   Expected: "Welcome, Test User!" (user is now registered)

PASS CRITERIA:
- ✓ Unregistered card triggers registration screen
- ✓ After successful registration, flow continues to next action (QR Scan)
- ✓ Registration data persists in database
- ✓ Payload (next_action) is correctly passed and used

═══════════════════════════════════════════════════════════════════════════════
TEST 6: REGISTRATION → CANCEL
═══════════════════════════════════════════════════════════════════════════════

1. Start at Main Menu

2. Tap "Open Doors" button
   In console, enter card ID: 888 (unregistered)
   Expected: Register User screen appears
   
3. Tap "Cancel" button
   Expected: Pops register screen
   Expected: Pops card scan screen  
   Expected: Returns to Main Menu

PASS CRITERIA:
- ✓ Cancel button returns to Main Menu
- ✓ No partial registration is saved

═══════════════════════════════════════════════════════════════════════════════
TEST 7: BASKET MANAGEMENT (Remove Item, Decrease Quantity)
═══════════════════════════════════════════════════════════════════════════════

1. Start borrow flow (Open Doors → Card 1 → QR Scan)

2. Scan item 1 three times (Coca Cola x3)
   Expected: Basket shows "1 items", Coca Cola with quantity 3
   
3. Scan item 2 once (Sprite x1)
   Expected: Basket shows "2 items"
   
4. Tap "Done" button
   Expected: Basket screen shows both items
   
5. On Coca Cola row, tap "−" (decrease) button
   Expected: Coca Cola quantity decreases to x2
   
6. On Sprite row, tap "✕" (remove) button
   Expected: Sprite is removed from basket
   Expected: Basket shows "1 items" (only Coca Cola x2)
   
7. Tap "← Back" button
   Expected: Returns to QR Scan screen
   Expected: Basket still has Coca Cola x2
   
8. Tap "Done" button again
   Expected: Basket screen shows Coca Cola x2
   
9. Tap "Confirm" button
   Expected: Transaction processed, Thank You screen appears

PASS CRITERIA:
- ✓ Basket item management works (remove, decrease quantity)
- ✓ Basket state persists when going back and forward
- ✓ Only confirmed items are processed

═══════════════════════════════════════════════════════════════════════════════
TEST 8: STOCK/INVENTORY (No Card Required)
═══════════════════════════════════════════════════════════════════════════════

1. Start at Main Menu

2. Tap "Stock/Inventory" button
   Expected: Inventory screen appears IMMEDIATELY (no card scan)
   Expected: Shows list of items with quantities
   Expected: Color-coded bars (green for high stock, red for low)
   
3. Tap "← Back" button
   Expected: Returns to Main Menu

PASS CRITERIA:
- ✓ Stock/Inventory does NOT require card scan
- ✓ Screen appears immediately
- ✓ Back button works correctly

═══════════════════════════════════════════════════════════════════════════════
TEST 9: SCREEN STACK DEPTH & LIFECYCLE HOOKS
═══════════════════════════════════════════════════════════════════════════════

This test verifies that:
- Screens are properly pushed and popped
- Only the top screen receives events
- on_enter() and on_exit() lifecycle hooks are called correctly

1. Start at Main Menu (stack depth: 1)
   
2. Tap "Open Doors" → Card Scan screen (stack depth: 2)
   
3. Enter card 1 → QR Scan screen (stack depth: 3)
   
4. Tap "← Back" → Card Scan screen (stack depth: 2)
   
5. Tap "← Back" → Main Menu (stack depth: 1)

PASS CRITERIA:
- ✓ Only one screen visible at any time
- ✓ Back button always returns to previous screen
- ✓ Lifecycle hooks called in correct order (check console if logging enabled)

═══════════════════════════════════════════════════════════════════════════════
TEST 10: MOCK INPUT VALUES
═══════════════════════════════════════════════════════════════════════════════

According to the requirements, items in inventory are given values 1, 2, ..., n
for mock scanning.

Database pre-populated with:
- Card 1: Admin User (user_id == 1, is_admin == True)
- Card 2: Alice Johnson (user_id == 2)
- Card 3: Bob Smith (user_id == 3)

- QR Code 1: Coca Cola
- QR Code 2: Sprite
- QR Code 3: Orange Juice
- QR Code 4: Water
- QR Code 5: Energy Drink
- QR Code 6: Iced Tea

Test scanning different QR codes (1-6) to verify all items can be scanned.

═══════════════════════════════════════════════════════════════════════════════
AUTOMATED TESTS
═══════════════════════════════════════════════════════════════════════════════

Run automated unit tests for ScreenManager:
```bash
cd /path/to/Sinine-kapp
python tests/navigation_test.py
```

Expected output:
- All 8 tests should pass
- Tests verify push/pop/go_to operations
- Tests verify lifecycle hooks
- Tests verify stack depth management

═══════════════════════════════════════════════════════════════════════════════
SUMMARY OF REQUIREMENTS VERIFICATION
═══════════════════════════════════════════════════════════════════════════════

✓ ScreenManager is stack-based with push/pop/go_to/current methods
✓ Only current (top) screen receives events and updates
✓ Screens render in correct Z-order (only top screen visible)
✓ Transitions (push/pop/go_to) behave predictably
✓ Card-scan → QR-scan → basket flow is correct
✓ Registration redirects back to attempted action
✓ Admin access is restricted to user_id == 1
✓ App runs fullscreen at 600x1024
✓ Uses mock inputs (keyboard entry in console)
✓ Items in inventory are numbered 1, 2, ..., n

╔══════════════════════════════════════════════════════════════════════════════╗
║                         HAPPY TESTING! 🎮                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
