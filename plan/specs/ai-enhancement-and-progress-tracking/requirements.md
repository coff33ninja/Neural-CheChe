# Requirements Document

## Introduction

This feature enhances the Neural CheChe AI training system with critical improvements to ensure fair gameplay, comprehensive progress tracking, and better user experience. The enhancement focuses on preventing illegal AI behavior (magical piece generation), implementing visual progress indicators for both CLI and GUI interfaces, maintaining detailed move history with JSON backup, and providing real-time scoring systems.

## Requirements

### Requirement 1

**User Story:** As a user training AI agents, I want to ensure the AI never generates illegal "magical pieces" during gameplay, so that the training remains fair and follows proper game rules.

#### Acceptance Criteria

1. WHEN the AI generates a move THEN the system SHALL validate that no new pieces are created beyond normal game rules
2. WHEN the AI attempts to place a piece not previously on the board THEN the system SHALL reject the move and log the violation
3. WHEN move validation occurs THEN the system SHALL only allow pieces that exist according to current board state and game rules
4. IF an AI attempts to generate a magical piece THEN the system SHALL force the AI to select a different legal move
5. WHEN training completes THEN the system SHALL provide a report of any illegal move attempts for analysis

### Requirement 2

**User Story:** As a user monitoring AI training progress, I want to see visual progress bars and generational growth indicators in both CLI and GUI, so that I can track training effectiveness in real-time.

#### Acceptance Criteria

1. WHEN training is running in CLI mode THEN the system SHALL display a tqdm-style progress bar showing current generation progress
2. WHEN training is running in GUI mode THEN the system SHALL display graphical progress indicators with generational growth metrics
3. WHEN a generation completes THEN the system SHALL update progress indicators to show cumulative improvement over time
4. WHEN displaying progress THEN the system SHALL include metrics like win rates, skill improvements, and training milestones
5. IF the window is resized THEN the GUI progress indicators SHALL adapt to maintain proper visibility and proportions

### Requirement 3

**User Story:** As a researcher analyzing AI behavior, I want comprehensive move choice history stored in JSON format with backup capabilities, so that I can review and analyze decision patterns over time.

#### Acceptance Criteria

1. WHEN an AI makes a move THEN the system SHALL record the move choice, board state, and decision context in JSON format
2. WHEN a game completes THEN the system SHALL save the complete move history to a timestamped JSON backup file
3. WHEN the system starts THEN the system SHALL create a backup directory structure for organizing historical data
4. WHEN storing move data THEN the system SHALL include metadata like generation number, agent type, game type, and evaluation scores
5. IF storage fails THEN the system SHALL attempt alternative backup locations and notify the user of any data loss risks

### Requirement 4

**User Story:** As a user tracking AI performance, I want real-time current score display and historical score tracking, so that I can monitor immediate performance and long-term trends.

#### Acceptance Criteria

1. WHEN a game is in progress THEN the system SHALL display current scores for both players in real-time
2. WHEN displaying scores THEN the system SHALL show both current game score and cumulative performance metrics
3. WHEN a generation completes THEN the system SHALL update and persist score history for trend analysis
4. WHEN the GUI is active THEN the system SHALL display score information in a clear, non-intrusive manner that adapts to window sizing
5. IF score calculation fails THEN the system SHALL use fallback scoring methods and log the issue for debugging

### Requirement 5

**User Story:** As a user watching AI games, I want to see captured pieces displayed for each AI player similar to traditional chess interfaces, so that I can easily track material advantage and game progression.

#### Acceptance Criteria

1. WHEN a piece is captured THEN the system SHALL add it to the capturing player's taken pieces display area
2. WHEN displaying captured pieces THEN the system SHALL organize them by piece type and show them in a dedicated UI section for each player
3. WHEN the GUI is active THEN the system SHALL show captured pieces alongside the game board in a clear, traditional chess game layout
4. WHEN pieces are captured THEN the system SHALL update the material advantage calculation and display it prominently
5. IF no pieces have been captured THEN the system SHALL show empty capture areas to maintain consistent UI layout

### Requirement 6

**User Story:** As a user with different screen sizes and preferences, I want the GUI to properly handle window sizing and maintain usability across different display configurations, so that I can use the system effectively on any device.

#### Acceptance Criteria

1. WHEN the application starts THEN the system SHALL detect screen resolution and set appropriate default window size
2. WHEN the user resizes the window THEN the system SHALL dynamically adjust all UI elements to maintain proper proportions
3. WHEN displaying on smaller screens THEN the system SHALL prioritize essential information and provide scrolling or collapsible sections as needed
4. WHEN window size changes THEN the system SHALL ensure progress bars, score displays, game boards, and captured pieces areas remain clearly visible
5. IF the window becomes too small THEN the system SHALL maintain minimum usability thresholds and warn the user if necessary