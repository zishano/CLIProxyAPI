package api

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/router-for-me/CLIProxyAPI/v8/sdk/api/handlers"
)

// credentialPinMiddleware resolves a public, non-secret auth index to the
// internal auth ID used by the scheduler. Missing headers preserve normal routing.
func (s *Server) credentialPinMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		requestedIndex := strings.TrimSpace(c.GetHeader(handlers.CredentialAuthIndexHeader))
		c.Request.Header.Del(handlers.CredentialAuthIndexHeader)
		if requestedIndex == "" {
			c.Next()
			return
		}
		if s == nil || s.handlers == nil || s.handlers.AuthManager == nil {
			c.AbortWithStatusJSON(http.StatusServiceUnavailable, gin.H{
				"error": gin.H{"message": "credential routing is unavailable", "type": "server_error"},
			})
			return
		}

		matchedID := ""
		for _, candidate := range s.handlers.AuthManager.List() {
			if candidate == nil || !strings.EqualFold(strings.TrimSpace(candidate.Index), requestedIndex) {
				continue
			}
			if matchedID != "" {
				c.AbortWithStatusJSON(http.StatusConflict, gin.H{
					"error": gin.H{"message": "credential auth index is ambiguous", "type": "invalid_request_error"},
				})
				return
			}
			matchedID = candidate.ID
		}
		if matchedID == "" {
			c.AbortWithStatusJSON(http.StatusNotFound, gin.H{
				"error": gin.H{"message": "credential auth index was not found", "type": "invalid_request_error"},
			})
			return
		}

		requestContext := handlers.WithPinnedAuthID(c.Request.Context(), matchedID)
		c.Request = c.Request.WithContext(requestContext)
		c.Next()
	}
}
