                                        if self.parent.game_board.magic_fruit_index:
                                            self.parent.game_board.eval_new_tile(button.id)
                                            self.parent.magic_eventing, magic_number, cell_pos = self.parent.game_board.magic_fruit_found()
                                            if self.parent.magic_eventing:
                                                utils.sound_play(sound=sfx.magic_fruit, volume=self.game.sfx_volume)
                                                if magic_number == 1:
                                                    self.parent.current_event = self.parent.magic_fruit1_event
                                                elif magic_number == 2:
                                                    self.parent.current_event = self.parent.magic_fruit2_event
                                                elif magic_number == 3:
                                                    self.parent.current_event = self.parent.magic_fruit3_event
                                                self.parent.game_board.board[cell_pos].magic_fruit = 0
                                                self.parent.magicing_number = magic_number
                                                current_score = getattr(self.parent, f'day{self.parent.current_day}_score')
                                                new_score = current_score + 1
                                                setattr(self.parent, f'day{self.parent.current_day}_score', new_score)
                                                setattr(self.parent, f'magic_fruit{magic_number}_event', None)
                                                self.parent.play_event_state= False
                                                self.exit_state()


                                    if self.parent.game_board.magic_fruit_index:
                                        self.parent.game_board.eval_new_tile(button.id)
                                        self.parent.magic_eventing, magic_number, cell_pos = self.parent.game_board.magic_fruit_found()
                                        if self.parent.magic_eventing:
                                            utils.sound_play(sound=sfx.magic_fruit, volume=self.game.sfx_volume)
                                            if magic_number == 1:
                                                self.parent.current_event = self.parent.magic_fruit1_event
                                            elif magic_number == 2:
                                                self.parent.current_event = self.parent.magic_fruit2_event
                                            elif magic_number == 3:
                                                self.parent.current_event = self.parent.magic_fruit3_event
                                            self.parent.game_board.board[cell_pos].magic_fruit = 0
                                            self.parent.magicing_number = magic_number
                                            current_score = getattr(self.parent, f'day{self.parent.current_day}_score')
                                            new_score = current_score + 1
                                            setattr(self.parent, f'day{self.parent.current_day}_score', new_score)
                                            setattr(self.parent, f'magic_fruit{magic_number}_event', None)
                                            self.parent.play_event_state= False
                                            self.exit_state()