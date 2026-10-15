class WelcomeController < ApplicationController

    def index
        @num_users = User.count
    end

end
