"""
Test the query rewriter with memory.
"""
from src.memory.memory_manager import MemoryManager
from src.graph.query_rewriter import QueryRewriter
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="test_rewriter")

def main():
    """Test query rewriting."""
    
    logger.log_info("Testing Query Rewriter with Memory")
    logger.log_info("=" * 60)
    
    # Setup
    memory = MemoryManager()
    rewriter = QueryRewriter()
    
    # Simulate conversation
    logger.log_info("\n📝 Simulating Conversation:\n")
    
    conversations = [
        ("What is the budget in Q2_Budget_Proposal.pdf?",
         "The budget is $45,000 for the storage vendor upgrade."),
        ("Who approved it?", None),
        ("What did she say?", None),
        ("Compare that with the earlier draft", None)
    ]
    
    for user_msg, assistant_msg in conversations:
        logger.log_info(f"\n👤 User: {user_msg}")
        
        # Get memory context
        context = memory.get_context_for_rewrite()
        
        # Rewrite query
        result = rewriter.rewrite(user_msg, context)
        
        logger.log_info(f"🔄 Rewritten: {result['rewritten_query']}")
        logger.log_info(f"💭 Reasoning: {result['reasoning']}")
        
        # Add to memory (with mock assistant response if provided)
        if assistant_msg:
            memory.add_turn(user_msg, assistant_msg)
        else:
            # Use rewritten query as context
            memory.add_turn(user_msg, f"[Answered about: {result['rewritten_query']}]")
    
    logger.log_info("\n" + "=" * 60)
    logger.log_info("Query Rewriter Test Complete!")

if __name__ == "__main__":
    main()