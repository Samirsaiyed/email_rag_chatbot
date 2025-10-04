"""
Test the memory system.
"""
from src.memory.memory_manager import MemoryManager
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="test_memory")

def main():
    """Test memory management."""
    
    logger.log_info("Testing Memory System")
    logger.log_info("=" * 60)
    
    # Create memory manager
    memory = MemoryManager(max_turns=5)
    
    # Simulate conversation
    conversations = [
        (
            "What is the budget in Q2_Budget_Proposal.pdf?",
            "The budget is $45,000 [msg: M-68e801dc, page: 2] for the storage vendor upgrade."
        ),
        (
            "Who approved it?",
            "Sarah Johnson from Finance approved the budget [msg: M-c3959d3e] during the meeting on April 10, 2001."
        ),
        (
            "What did she say about the timeline?",
            "She mentioned that John should finalize the vendor contract [msg: M-a2715587]."
        )
    ]
    
    for user_msg, assistant_msg in conversations:
        logger.log_info(f"\n👤 User: {user_msg}")
        logger.log_info(f"🤖 Assistant: {assistant_msg}")
        
        memory.add_turn(user_msg, assistant_msg)
    
    # Get context
    logger.log_info("\n" + "=" * 60)
    logger.log_info("Memory State:")
    logger.log_info("=" * 60)
    
    context = memory.get_context_for_rewrite()
    
    logger.log_info("\n📜 Conversation History:")
    logger.log_info(context['conversation_history'])
    
    logger.log_info("\n🏷️  Extracted Entities:")
    for entity_type, values in context['entities'].items():
        if values:
            logger.log_info(f"  {entity_type}: {values}")
    
    logger.log_info("\n🎯 Last Mentioned:")
    for entity_type, value in context['last_mentioned'].items():
        if value:
            logger.log_info(f"  {entity_type}: {value}")
    
    logger.log_info("\n" + "=" * 60)
    logger.log_info("Memory Test Complete!")

if __name__ == "__main__":
    main()