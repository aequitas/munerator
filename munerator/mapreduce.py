"""
Reduce map into a playlist of most populair games to be played based current player votes, num. players, etc.
"""


def populate_playlist():
    pass

# votes mapreduce
# db.votes.mapReduce(
#     function(){
#         emit(this.mapname, this.vote)
#     },
#     function(key, values){
#         return 1,Array.sum(values)
#     },
#     {
#         query:{
#             gamemap:{
#                 $exists:true
#             }
#         },
#         out:{
#             inline:1
#         }
#     }
# )
