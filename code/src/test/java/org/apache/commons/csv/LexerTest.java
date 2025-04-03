package org.apache.commons.csv;

import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import static org.junit.jupiter.api.Assertions.*;
import org.mockito.*;
import static org.mockito.Mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;
import java.io.IOException;

@ExtendWith(MockitoExtension.class)
class LexerTest {
    @Mock
    private ExtendedBufferedReader reader;
    
    @Mock
    private CSVFormat format;
    
    private Lexer lexer;
    private Token token;

    @BeforeAll
    static void setupBeforeAll() {
        // Initialize any static resources if needed
    }

    @BeforeEach
    void setupBeforeEach() throws IOException {
        // Setup default CSV format behavior
        when(format.getDelimiterCharArray()).thenReturn(new char[]{','});
        when(format.getEscapeCharacter()).thenReturn('\\');
        when(format.getQuoteCharacter()).thenReturn('"');
        when(format.getCommentMarker()).thenReturn('#');
        when(format.getIgnoreSurroundingSpaces()).thenReturn(false);
        when(format.getIgnoreEmptyLines()).thenReturn(false);
        when(format.getLenientEof()).thenReturn(false);
        when(format.getTrailingData()).thenReturn(false);
        
        // Initialize lexer with mocked dependencies
        lexer = new Lexer(format, reader);
        
        // Initialize test token
        token = new Token();
    }

    @AfterEach
    void teardownAfterEach() throws IOException {
        // Reset mocks if needed
        Mockito.reset(reader, format);
        
        // Clean up lexer if it's stateful
        if (lexer != null) {
            lexer.close();
        }
    }

    @AfterAll
    static void teardownAfterAll() {
        // Clean up any static resources if needed
    }

    @Test
    @DisplayName("Should handle double quote characters by adding single quote to token")
    void parseEncapsulatedToken_WhenDoubleQuoteEncountered_AddsSingleQuoteToToken() throws IOException {
        // Arrange
        when(reader.read()).thenReturn((int) '"', (int) '"', (int) ',');
        when(reader.peek()).thenReturn((int) '"');
        when(lexer.isQuoteChar('"')).thenReturn(true);
        when(lexer.isDelimiter(',')).thenReturn(true);

        // Act
        Token result = lexer.parseEncapsulatedToken(token);

        // Assert
        assertEquals("\"", result.content.toString());
        assertEquals(Token.Type.TOKEN, result.type);
        assertTrue(result.isQuoted);
    }

    @Test
    @DisplayName("Should return TOKEN type when delimiter is encountered after quote")
    void parseEncapsulatedToken_WhenDelimiterAfterQuote_ReturnsTokenType() throws IOException {
        // Arrange
        when(reader.read()).thenReturn((int) '"', (int) ',');
        when(lexer.isQuoteChar('"')).thenReturn(true);
        when(lexer.isDelimiter(',')).thenReturn(true);

        // Act
        Token result = lexer.parseEncapsulatedToken(token);

        // Assert
        assertEquals(Token.Type.TOKEN, result.type);
        assertTrue(result.isQuoted);
    }

    @Test
    @DisplayName("Should return EOF type when EOF is encountered after quote")
    void parseEncapsulatedToken_WhenEOFAfterQuote_ReturnsEOFType() throws IOException {
        // Arrange
        when(reader.read()).thenReturn((int) '"', IOUtils.EOF);
        when(lexer.isQuoteChar('"')).thenReturn(true);
        when(lexer.isEndOfFile(IOUtils.EOF)).thenReturn(true);

        // Act
        Token result = lexer.parseEncapsulatedToken(token);

        // Assert
        assertEquals(Token.Type.EOF, result.type);
        assertTrue(result.isReady);
        assertTrue(result.isQuoted);
    }

    @Test
    @DisplayName("Should return EORECORD type when end of line is encountered after quote")
    void parseEncapsulatedToken_WhenEndOfLineAfterQuote_ReturnsEORECORDType() throws IOException {
        // Arrange
        when(reader.read()).thenReturn((int) '"', (int) '\n');
        when(lexer.isQuoteChar('"')).thenReturn(true);
        when(lexer.readEndOfLine('\n')).thenReturn(true);

        // Act
        Token result = lexer.parseEncapsulatedToken(token);

        // Assert
        assertEquals(Token.Type.EORECORD, result.type);
        assertTrue(result.isQuoted);
    }

    @Test
    @DisplayName("Should throw exception when invalid character is encountered after quote")
    void parseEncapsulatedToken_WhenInvalidCharAfterQuote_ThrowsCSVException() throws IOException {
        // Arrange
        when(reader.read()).thenReturn((int) '"', (int) 'x');
        when(lexer.isQuoteChar('"')).thenReturn(true);
        when(lexer.isDelimiter('x')).thenReturn(false);
        when(lexer.isEndOfFile('x')).thenReturn(false);
        when(lexer.readEndOfLine('x')).thenReturn(false);
        when(lexer.getCurrentLineNumber()).thenReturn(1L);
        when(lexer.getCharacterPosition()).thenReturn(1L);

        // Act & Assert
        assertThrows(CSVException.class, () -> lexer.parseEncapsulatedToken(token));
    }

    @Test
    @DisplayName("Should append escaped character when escape character is encountered")
    void parseEncapsulatedToken_WhenEscapeChar_AppendsEscapedCharacter() throws IOException {
        // Arrange
        when(reader.read()).thenReturn((int) '\\', (int) '"', (int) ',');
        when(lexer.isEscape('\\')).thenReturn(true);
        when(lexer.isQuoteChar('"')).thenReturn(true);
        when(lexer.isDelimiter(',')).thenReturn(true);
        doAnswer(invocation -> {
            Token t = invocation.getArgument(0);
            t.content.append('\\');
            return null;
        }).when(lexer).appendNextEscapedCharacterToToken(any(Token.class));

        // Act
        Token result = lexer.parseEncapsulatedToken(token);

        // Assert
        assertEquals("\\", result.content.toString());
        assertEquals(Token.Type.TOKEN, result.type);
        assertTrue(result.isQuoted);
    }

    @Test
    @DisplayName("Should throw exception when EOF is reached before token finishes (lenientEof false)")
    void parseEncapsulatedToken_WhenPrematureEOF_ThrowsCSVException() throws IOException {
        // Arrange
        when(reader.read()).thenReturn(IOUtils.EOF);
        when(lexer.isEndOfFile(IOUtils.EOF)).thenReturn(true);
        when(lexer.getCurrentLineNumber()).thenReturn(1L);

        // Act & Assert
        assertThrows(CSVException.class, () -> lexer.parseEncapsulatedToken(token));
    }

    @Test
    @DisplayName("Should return EOF type when EOF is reached before token finishes (lenientEof true)")
    void parseEncapsulatedToken_WhenPrematureEOFWithLenientEof_ReturnsEOFType() throws IOException {
        // Arrange
        when(format.getLenientEof()).thenReturn(true);
        lexer = new Lexer(format, reader);
        when(reader.read()).thenReturn(IOUtils.EOF);
        when(lexer.isEndOfFile(IOUtils.EOF)).thenReturn(true);

        // Act
        Token result = lexer.parseEncapsulatedToken(token);

        // Assert
        assertEquals(Token.Type.EOF, result.type);
        assertTrue(result.isReady);
        assertTrue(result.isQuoted);
    }

    @Test
    @DisplayName("Should append regular characters to token content")
    void parseEncapsulatedToken_WhenRegularCharacter_AppendsToTokenContent() throws IOException {
        // Arrange
        when(reader.read()).thenReturn((int) 'a', (int) 'b', (int) '"', (int) ',');
        when(lexer.isQuoteChar('"')).thenReturn(true);
        when(lexer.isDelimiter(',')).thenReturn(true);

        // Act
        Token result = lexer.parseEncapsulatedToken(token);

        // Assert
        assertEquals("ab", result.content.toString());
        assertEquals(Token.Type.TOKEN, result.type);
        assertTrue(result.isQuoted);
    }

    @Test
    @DisplayName("Should handle trailing data when trailingData is true")
    void parseEncapsulatedToken_WhenTrailingDataTrue_AppendsNonWhitespaceChars() throws IOException {
        // Arrange
        when(format.getTrailingData()).thenReturn(true);
        lexer = new Lexer(format, reader);
        when(reader.read()).thenReturn((int) '"', (int) 'x', (int) ',');
        when(lexer.isQuoteChar('"')).thenReturn(true);
        when(lexer.isDelimiter(',')).thenReturn(true);

        // Act
        Token result = lexer.parseEncapsulatedToken(token);

        // Assert
        assertEquals("x", result.content.toString());
        assertEquals(Token.Type.TOKEN, result.type);
        assertTrue(result.isQuoted);
    }

    @Test
    @DisplayName("Should handle whitespace after quote when trailingData is false")
    void parseEncapsulatedToken_WhenWhitespaceAfterQuoteWithTrailingDataFalse_IgnoresWhitespace() throws IOException {
        // Arrange
        when(reader.read()).thenReturn((int) '"', (int) ' ', (int) ',');
        when(lexer.isQuoteChar('"')).thenReturn(true);
        when(lexer.isDelimiter(',')).thenReturn(true);

        // Act
        Token result = lexer.parseEncapsulatedToken(token);

        // Assert
        assertEquals("", result.content.toString());
        assertEquals(Token.Type.TOKEN, result.type);
        assertTrue(result.isQuoted);
    }
}