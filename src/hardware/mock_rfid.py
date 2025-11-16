# src/hardware/mock_rfid.py
class MockRFIDReader:
    def __init__(self):
        self.ui_manager = None
        self.screen_manager = None
        self._pending_result = None
        self._waiting_for_input = False
    
    def set_managers(self, ui_manager, screen_manager):
        """Set references to UI and screen managers for popup dialogs"""
        self.ui_manager = ui_manager
        self.screen_manager = screen_manager
    
    def read(self):
        """
        Read RFID card. If managers are set, shows on-screen dialog.
        Otherwise falls back to terminal input.
        """
        if self.ui_manager and self.screen_manager:
            # Use on-screen input dialog
            return self._read_with_dialog()
        else:
            # Fallback to terminal input
            try:
                uid = input("MOCK: enter RFID UID (or blank to cancel): ").strip()
                return uid if uid else None
            except Exception:
                return None
    
    def _read_with_dialog(self):
        """Show input dialog and wait for result"""
        import pygame
        from screens.input_dialog import InputDialogScreen
        
        self._pending_result = None
        self._waiting_for_input = True
        
        # Create callback to capture result
        def on_input_complete(value):
            self._pending_result = value
            self._waiting_for_input = False
        
        # Create and push input dialog
        dialog = InputDialogScreen(
            self.ui_manager,
            self.screen_manager,
            title="Scan ID Card",
            placeholder="Enter card ID",
            callback=on_input_complete
        )
        self.screen_manager.push(dialog, payload={
            'title': "Scan ID Card", 
            'placeholder': "Enter card ID",
            'callback': on_input_complete
        })
        
        # Wait for user input by running event loop
        clock = pygame.time.Clock()
        while self._waiting_for_input:
            dt = clock.tick(30) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._waiting_for_input = False
                    self._pending_result = None
                    break
                self.screen_manager.handle_event(event)
            
            # Update and render
            self.screen_manager.update(dt)
            self.screen_manager.render(self.ui_manager.screen)
            pygame.display.flip()
        
        # Return the result (could be None if cancelled)
        result = self._pending_result
        if result == "":
            return None
        return result
