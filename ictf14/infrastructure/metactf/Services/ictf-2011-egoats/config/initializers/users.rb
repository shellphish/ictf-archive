scheduler = Rufus::Scheduler.start_new
scheduler.every("5m") do
  User.where('created_at < DATE_SUB(NOW(), INTERVAL 30 MINUTE)').all
end
