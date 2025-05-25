# Pinecone gRPC Implementation

The Nivaran AI application now uses Pinecone's gRPC client for improved performance in vector database operations.

## What Changed

The vector store implementation in `app/utils/vector_store.py` has been updated to use the gRPC client:

1. Changed the import from `pinecone import Pinecone` to `from pinecone.grpc import PineconeGRPC as Pinecone`

2. Added optimized connection pooling with `pool_threads=50` to improve parallel processing performance

3. Added a new `query_namespaces()` method that efficiently queries across multiple namespaces in parallel

4. Enhanced logging to track gRPC connection and performance

## Benefits

Using the gRPC client provides several benefits:

- **Faster data operations**: gRPC is more efficient than HTTP for data operations such as upserts and queries
- **Lower latency**: Reduced overhead in the communication protocol
- **Better parallelization**: Optimized for concurrent operations with proper connection pooling
- **Cross-namespace capabilities**: Easy querying across multiple namespaces with combined ranking

## Requirements

The application already includes the necessary dependency in requirements.txt:

```
pinecone[grpc]>=6.0.2
```

## Implementation Details

### Connection Initialization

```python
# Initialize Pinecone with the v6+ gRPC API for better performance
self.pinecone_client = Pinecone(
    api_key=self.pinecone_api_key
)

# Get index by name with optimized pool_threads for better performance
self.index = self.pinecone_client.Index(
    name=self.index_name,
    pool_threads=50  # Optimize for parallel processing
)
```

### New Cross-Namespace Functionality

```python
def query_namespaces(self, vector, namespaces, top_k=5, filter=None, include_metadata=True):
    """
    Query across multiple namespaces and return combined results.
    Uses parallelization for better performance.
    """
    return self.index.query_namespaces(
        vector=vector,
        namespaces=namespaces,
        top_k=top_k,
        include_metadata=include_metadata,
        filter=filter,
        show_progress=False
    )
```

## Performance Notes

- The optimal `pool_threads` value (currently set to 50) may need to be adjusted based on your specific workload and available resources
- For large-scale operations, consider implementing batching for upserts to minimize network overhead
- Using filters in queries can still impact performance, so try to be as specific as possible with filters
