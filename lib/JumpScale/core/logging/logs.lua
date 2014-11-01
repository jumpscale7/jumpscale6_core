if redis.call("LLEN", "logs.queue") > 2000 then
    redis.call("LPOP", "logs.queue")
end

redis.call("RPUSH", "logs.queue",ARGV[1])
return "OK"

